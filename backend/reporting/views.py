from datetime import date, timedelta

from django.db.models import Count, Q, Sum
from rest_framework import status as http_status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Department, User
from assets.models import (TERMINAL_STATUSES, AmcContract, Asset, AssetCheckout,
                           AssetTransfer, ServiceRecord)
from assets.serializers import AssetSerializer, CheckoutSerializer, TransferSerializer
from catalog.models import Category, Vendor
from core.models import Setting
from core.permissions import HasRolePermission, can_read_audit, is_admin
from core.retention import ip_is_expired
from core.services import get_profile, log_action


# ---------- Dashboard / charts ----------

EXPIRY_THRESHOLD_DAYS = (7, 15, 30)


class DashboardView(APIView):
    """Read-only operational summary.

    Declared as an APIView rather than @api_view so HasRolePermission can read
    ``required_permission`` off the view: for a function-based view it finds no
    permission_map and no required_permission, falls through to code=None, and
    lets any authenticated request pass — including one from a Disabled profile
    whose token was never revoked.
    """

    permission_classes = [HasRolePermission]
    required_permission = "asset_view"

    def get(self, request):
        return Response(build_dashboard(visible_assets(request)))


def visible_assets(request, include_terminal=False):
    """The Asset rows this reader may also read one at a time.

    Every dashboard figure is derived from this queryset, so no aggregate can
    summarize records the reader could not open individually (decision C6 applied
    to B9). A global reader gets the whole register.

    B9 FR-017 excludes `Sold`, `Scrapped`, and `Lost` by default, because a terminal
    Asset has left circulation and counting it overstates what the organization holds —
    total value most visibly. A surface whose stated purpose *is* terminal passes
    `include_terminal=True` and says so on the surface itself.
    """
    qs = Asset.objects.all()
    profile = get_profile(request)
    if profile is not None and profile.has_own_records_scope():
        qs = qs.filter(custodian=profile)
    if not include_terminal:
        qs = qs.exclude(status__in=TERMINAL_STATUSES)
    return qs


def build_dashboard(qs):
    today = date.today()
    soon = today + timedelta(days=30)

    kpis = {
        "total_assets": qs.count(),
        "active": qs.filter(status__in=["Available", "Assigned"]).count(),
        "available": qs.filter(status="Available").count(),
        "assigned": qs.filter(status="Assigned").count(),
        "repair": qs.filter(status="Under Repair").count(),
        "total_value": float(qs.aggregate(v=Sum('purchase_cost'))['v'] or 0),
        "open_checkouts": AssetCheckout.objects.filter(status="Open", asset__in=qs).count(),
        "pending_transfers": AssetTransfer.objects.filter(status="Pending", asset__in=qs).count(),
        "open_services": ServiceRecord.objects.filter(status="Open", asset__in=qs).count(),
        "warranty_expired": qs.filter(warranty_end__lt=today).count(),
        "amc_expired": AmcContract.objects.filter(
            status="Active", end_date__lt=today, asset__in=qs).count(),
    }
    # Disjoint bands, not cumulative counts (FR-018): an Asset 5 days from expiry
    # belongs to the 7-day band and to no other, so the tiles read as a workload
    # breakdown that sums to the total rather than three overlapping views of it. A
    # boundary date belongs to the narrower band, and coverage beyond the widest band
    # is excluded rather than absorbed (FR-019).
    lower = today
    for days in EXPIRY_THRESHOLD_DAYS:
        until = today + timedelta(days=days)
        kpis[f"warranty_expiring_{days}"] = qs.filter(
            warranty_end__gte=lower, warranty_end__lte=until).count()
        kpis[f"amc_expiring_{days}"] = AmcContract.objects.filter(
            status="Active", end_date__gte=lower, end_date__lte=until,
            asset__in=qs).count()
        lower = until + timedelta(days=1)
    kpis["expiry_bands_are_disjoint"] = True

    recent_transfers = TransferSerializer(
        AssetTransfer.objects.filter(asset__in=qs)
        .select_related('asset', 'new_owner', 'previous_owner')
        .order_by('-transfer_date')[:5], many=True).data
    open_checkouts = CheckoutSerializer(
        AssetCheckout.objects.filter(status="Open", asset__in=qs)
        .select_related('asset', 'user')
        .order_by('-checkout_date')[:5], many=True).data
    expiring_assets = AssetSerializer(
        qs.filter(warranty_end__range=(today, soon))
        .order_by('warranty_end')[:5], many=True).data
    return {"kpis": kpis, "recent_transfers": recent_transfers,
            "open_checkouts": open_checkouts, "expiring_assets": expiring_assets}


def _last_12_months():
    months = []
    first = date.today().replace(day=1)
    for i in range(11, -1, -1):
        y, m = first.year, first.month - i
        while m <= 0:
            m += 12
            y -= 1
        months.append((y, m))
    return months


class ChartView(APIView):
    """Dashboard chart data. Same authorization contract as DashboardView."""

    permission_classes = [HasRolePermission]
    required_permission = "asset_view"

    def get(self, request, name):
        # The status distribution exists to show the whole register, which FR-017 names
        # as the case where terminal Assets are included — and requires the surface to
        # say so rather than leave the reader to infer it.
        whole_register = name == "status-distribution"
        response = build_chart(name, visible_assets(request, include_terminal=whole_register))
        if whole_register and hasattr(response, "data") and isinstance(response.data, dict):
            response.data["includes_terminal"] = True
            response.data["scope_note"] = (
                "Includes Sold, Scrapped, and Lost assets: this chart shows the whole "
                "register.")
        return response


def build_chart(name, assets):
    if name == "category-distribution":
        rows = (Category.objects.annotate(n=Count('asset', filter=Q(asset__in=assets)))
                .filter(n__gt=0).values_list('category_name', 'n'))
        return Response({"labels": [r[0] for r in rows], "data": [r[1] for r in rows]})

    if name == "status-distribution":
        rows = assets.values('status').annotate(n=Count('id')).order_by()
        return Response({"labels": [r['status'] for r in rows],
                         "data": [r['n'] for r in rows]})

    if name == "department-usage":
        rows = (Department.objects.annotate(n=Count('asset', filter=Q(asset__in=assets)))
                .values_list('name', 'n'))
        return Response({"labels": [r[0] for r in rows], "data": [r[1] for r in rows]})

    if name == "purchase-trend":
        labels, data = [], []
        for y, m in _last_12_months():
            start = date(y, m, 1)
            end = date(y + (m == 12), (m % 12) + 1, 1)
            total = (assets
                     .filter(procurement__purchase_date__gte=start,
                             procurement__purchase_date__lt=end)
                     .aggregate(v=Sum('purchase_cost'))['v'] or 0)
            labels.append(start.strftime("%b %y"))
            data.append(round(float(total), 2))
        return Response({"labels": labels, "data": data})

    if name == "transfer-trend":
        labels, data = [], []
        for y, m in _last_12_months():
            start = date(y, m, 1)
            end = date(y + (m == 12), (m % 12) + 1, 1)
            count = AssetTransfer.objects.filter(
                transfer_date__date__gte=start, transfer_date__date__lt=end,
                status="Approved", asset__in=assets).count()
            labels.append(start.strftime("%b %y"))
            data.append(count)
        return Response({"labels": labels, "data": data})

    if name == "warranty-timeline":
        today = date.today()
        buckets = [("Expired", None, None), ("0-30 days", 0, 30), ("31-60 days", 31, 60),
                   ("61-90 days", 61, 90), ("90+ days", 91, None)]
        labels, data = [], []
        for label, lo, hi in buckets:
            q = assets.filter(warranty_end__isnull=False)
            if label == "Expired":
                q = q.filter(warranty_end__lt=today)
            else:
                q = q.filter(warranty_end__gte=today + timedelta(days=lo))
                if hi is not None:
                    q = q.filter(warranty_end__lte=today + timedelta(days=hi))
            labels.append(label)
            data.append(q.count())
        return Response({"labels": labels, "data": data})

    if name == "amc-timeline":
        today = date.today()
        buckets = [("Expired", None, None), ("0-30 days", 0, 30), ("31-60 days", 31, 60),
                   ("61-90 days", 61, 90), ("90+ days", 91, None)]
        labels, data = [], []
        for label, lo, hi in buckets:
            q = AmcContract.objects.filter(status="Active", asset__in=assets)
            if label == "Expired":
                q = q.filter(end_date__lt=today)
            else:
                q = q.filter(end_date__gte=today + timedelta(days=lo))
                if hi is not None:
                    q = q.filter(end_date__lte=today + timedelta(days=hi))
            labels.append(label)
            data.append(q.count())
        return Response({"labels": labels, "data": data})

    return Response({"detail": "Unknown chart."}, status=http_status.HTTP_404_NOT_FOUND)


# ---------- Reports ----------

def _report_register():
    rows = []
    for a in Asset.objects.select_related('category', 'custodian', 'department', 'location').order_by('id'):
        rows.append([a.asset_id, a.tag_number, a.name or "-",
                     a.category.category_name if a.category else "-",
                     a.serial_number,
                     a.custodian.user_name if a.custodian else "-",
                     a.department.name if a.department else "-",
                     a.location.name if a.location else "-",
                     a.status, float(a.purchase_cost or 0)])
    return (["Asset ID", "Tag No", "Name", "Category", "Serial No", "Custodian",
             "Department", "Location", "Status", "Value"], rows)


def _report_movement():
    rows = []
    for t in AssetTransfer.objects.select_related('asset', 'previous_owner', 'new_owner', 'approved_by').order_by('-transfer_date'):
        rows.append([f"TRF-{t.id:05d}", t.asset.asset_id, t.asset.name or "-",
                     # An absent previous holder is an absence, not a party. Naming a
                     # store here invented a custodian that may never have existed and
                     # read identically to a Transfer that genuinely came from one.
                     t.previous_owner.user_name if t.previous_owner else "— none recorded",
                     t.new_owner.user_name if t.new_owner else "-",
                     t.transfer_date.strftime("%d-%b-%Y") if t.transfer_date else "-",
                     t.approved_by.user_name if t.approved_by else "-", t.status])
    return (["Transfer ID", "Asset ID", "Asset", "Previous User", "New User",
             "Date", "Approved By", "Status"], rows)


def _report_warranty():
    rows = []
    for a in Asset.objects.filter(warranty_end__isnull=False).select_related('category').order_by('warranty_end'):
        days = a.warranty_days_left
        rows.append([a.asset_id, a.name or "-",
                     a.category.category_name if a.category else "-",
                     a.warranty_start.strftime("%d-%b-%Y") if a.warranty_start else "-",
                     a.warranty_end.strftime("%d-%b-%Y"),
                     "Expired" if days < 0 else f"{days} days left"])
    return (["Asset ID", "Name", "Category", "Warranty Start", "Warranty End", "Status"], rows)


def _report_purchase():
    rows = []
    for a in Asset.objects.filter(procurement__isnull=False).select_related('procurement__vendor', 'brand', 'model').order_by('-procurement__purchase_date'):
        rows.append([a.asset_id, a.name or "-", a.procurement.vendor.name,
                     a.procurement.purchase_date.strftime("%d-%b-%Y"),
                     float(a.purchase_cost or 0),
                     a.brand.brand_name if a.brand else "-",
                     a.model.model_name if a.model else "-"])
    return (["Asset ID", "Name", "Vendor", "Purchase Date", "Cost", "Brand", "Model"], rows)


def _report_employee():
    rows = []
    for u in User.objects.filter(status="Active").select_related('department').order_by('user_name'):
        for a in u.held_assets.select_related('category'):
            rows.append([u.user_name, u.department.name if u.department else "-",
                         a.asset_id, a.name or "-",
                         a.category.category_name if a.category else "-",
                         a.status, a.condition])
    return (["Employee", "Department", "Asset ID", "Asset", "Category", "Status", "Condition"], rows)


def _report_audit():
    from core.models import AuditLog
    rows = []
    for log in AuditLog.objects.order_by('-date')[:1000]:
        # B9 FR-010: a source address past B8's six-month window is not served, whether
        # or not the retention job has run since the process started.
        address = "" if ip_is_expired(log.date) else log.ip_address
        rows.append([log.date.strftime("%d-%b-%Y %H:%M"), log.username, log.action,
                     log.module, log.old_value or "-", log.new_value or "-",
                     address or "-"])
    return (["Date", "User", "Action", "Module", "Old Value", "New Value", "IP Address"], rows)


def _report_in_service():
    rows = []
    for s in ServiceRecord.objects.filter(status="Open").select_related('asset', 'vendor').order_by('sent_date'):
        rows.append([s.asset.asset_id, s.asset.name or "-", s.vendor.name,
                     s.sent_date.strftime("%d-%b-%Y"),
                     s.expected_return_date.strftime("%d-%b-%Y") if s.expected_return_date else "-",
                     s.reason or "-"])
    return (["Asset ID", "Asset", "Vendor", "Sent Date", "Expected Return", "Reason"], rows)


def _report_vendor_service():
    rows = []
    for v in Vendor.objects.all().order_by('name'):
        records = ServiceRecord.objects.filter(vendor=v)
        pending = records.filter(status="Open").count()
        closed = records.filter(status="Closed")
        total_spend = closed.aggregate(v=Sum('cost'))['v'] or 0
        turnarounds = [(r.returned_date.date() - r.sent_date.date()).days
                       for r in closed if r.returned_date]
        avg_turnaround = round(sum(turnarounds) / len(turnarounds), 1) if turnarounds else "-"
        if not records.exists():
            continue
        rows.append([v.name, pending, closed.count(), float(total_spend), avg_turnaround])
    return (["Vendor", "Pending Repairs", "Completed Repairs", "Total Spend",
             "Avg Turnaround (days)"], rows)


def _report_amc_expiry():
    rows = []
    for c in AmcContract.objects.select_related('asset__category', 'vendor').order_by('end_date'):
        if not c.start_date or not c.end_date:
            # Incomplete (dates never entered) or Ended before dates were ever set —
            # either way there's no date range to compute an expiry from.
            expiry = ("Incomplete — dates not entered" if c.status != "Ended"
                      else "Cancelled before dates were entered")
            start, end = "-", "-"
        else:
            days = (c.end_date - date.today()).days
            expiry = "Ended" if c.status == "Ended" else ("Expired" if days < 0 else f"{days} days left")
            start, end = c.start_date.strftime("%d-%b-%Y"), c.end_date.strftime("%d-%b-%Y")
        rows.append([c.asset.asset_id, c.asset.name or "-",
                     c.asset.category.category_name if c.asset.category else "-",
                     c.vendor.name if c.vendor else "-",
                     start, end, c.status, expiry])
    return (["Asset ID", "Name", "Category", "Vendor", "AMC Start", "AMC End",
             "AMC Status", "Expiry"], rows)


def _report_lost():
    rows = []
    for a in Asset.objects.filter(status="Lost").select_related('custodian', 'department').order_by('asset_id'):
        rows.append([a.asset_id, a.name or "-",
                     a.custodian.user_name if a.custodian else "-",
                     a.department.name if a.department else "-",
                     a.condition])
    return (["Asset ID", "Name", "Last Known Custodian", "Department", "Condition"], rows)


# This report serves the same AuditLog rows as the /audit/ endpoint, including actor
# identity and source IP, so reaching it through report_access — which IT Staff and
# Viewer also hold — was a way around that endpoint's gate. Both surfaces now apply the
# same `audit_access` code (B8 ALR-003: Admin and IT Manager), so widening access is one
# grant rather than two edits that can drift apart.
AUDIT_REPORTS = {"audit"}

REPORTS = {
    "register": ("Asset Register Report", _report_register),
    "movement": ("Asset Movement Report", _report_movement),
    "warranty": ("Warranty Expiry Report", _report_warranty),
    "purchase": ("Purchase Report", _report_purchase),
    "employee": ("Employee Asset Report", _report_employee),
    "audit": ("Operational Event History", _report_audit),
    "in_service": ("Assets Currently In Service Report", _report_in_service),
    "vendor_service": ("Vendor Service Report", _report_vendor_service),
    "amc_expiry": ("AMC Expiry Report", _report_amc_expiry),
    "lost": ("Lost Assets Report", _report_lost),
}


class ReportView(APIView):
    permission_classes = [HasRolePermission]
    required_permission = "report_access"

    def get(self, request, key=None):
        if key is None:
            return Response({"reports": [
                {"key": k, "title": title} for k, (title, _) in REPORTS.items()
                if k not in AUDIT_REPORTS or can_read_audit(request)]})
        if key not in REPORTS:
            return Response({"detail": "Unknown report."}, status=http_status.HTTP_404_NOT_FOUND)
        if key in AUDIT_REPORTS and not can_read_audit(request):
            # The refusal is audited by core.middleware.AuditDenialMiddleware, which
            # runs outside this request's transaction — DRF rolls back anything written
            # while refusing.
            return Response({"detail": "You do not have permission to read this report."},
                            status=http_status.HTTP_403_FORBIDDEN)
        title, fn = REPORTS[key]
        headers, rows = fn()
        if key in AUDIT_REPORTS:
            log_action(request, "Report View", "Reports", new_value=key)
        return Response({"key": key, "title": title, "headers": headers, "rows": rows})


class ReportExportView(APIView):
    permission_classes = [HasRolePermission]
    required_permission = "report_access"

    def get(self, request, key, fmt):
        from django.http import FileResponse

        from core.exports import build_csv, build_excel, build_table_pdf
        if key not in REPORTS or fmt not in ("pdf", "excel", "csv"):
            return Response({"detail": "Unknown report or format."},
                            status=http_status.HTTP_404_NOT_FOUND)
        if key in AUDIT_REPORTS and not can_read_audit(request):
            return Response({"detail": "You do not have permission to export this report."},
                            status=http_status.HTTP_403_FORBIDDEN)
        title, fn = REPORTS[key]
        headers, rows = fn()
        company = Setting.get("company_name", "Cloud Shoe Factory")
        log_action(request, "Report Export", "Reports", new_value=f"{key} ({fmt})")
        if fmt == "pdf":
            buf = build_table_pdf(title, headers, rows, company_name=company)
            return FileResponse(buf, as_attachment=True, content_type='application/pdf',
                                filename=f"{key}_report.pdf")
        if fmt == "csv":
            buf = build_csv(title, headers, rows, company_name=company)
            return FileResponse(buf, as_attachment=True, content_type='text/csv',
                                filename=f"{key}_report.csv")
        buf = build_excel(title, headers, rows, company_name=company)
        return FileResponse(
            buf, as_attachment=True,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=f"{key}_report.xlsx")

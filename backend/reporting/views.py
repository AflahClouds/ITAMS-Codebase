from datetime import date, timedelta

from django.db.models import Count, Sum
from rest_framework import status as http_status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Department, User
from assets.models import Asset, AssetCheckout, AssetTransfer, ServiceRecord
from assets.serializers import AssetSerializer, CheckoutSerializer, TransferSerializer
from catalog.models import Category, Vendor
from core.models import Setting
from core.permissions import HasRolePermission
from core.services import log_action


# ---------- Dashboard / charts ----------

EXPIRY_THRESHOLD_DAYS = (7, 15, 30)


@api_view(['GET'])
def dashboard(request):
    today = date.today()
    soon = today + timedelta(days=30)
    qs = Asset.objects

    kpis = {
        "total_assets": qs.count(),
        "active": qs.filter(status__in=["Available", "Assigned"]).count(),
        "available": qs.filter(status="Available").count(),
        "assigned": qs.filter(status="Assigned").count(),
        "repair": qs.filter(status="Under Repair").count(),
        "total_value": float(qs.aggregate(v=Sum('purchase_cost'))['v'] or 0),
        "open_checkouts": AssetCheckout.objects.filter(status="Open").count(),
        "pending_transfers": AssetTransfer.objects.filter(status="Pending").count(),
        "open_services": ServiceRecord.objects.filter(status="Open").count(),
        "warranty_expired": qs.filter(warranty_end__lt=today).count(),
        "amc_expired": qs.filter(has_amc=True, amc_status="Active", amc_end__lt=today).count(),
    }
    for days in EXPIRY_THRESHOLD_DAYS:
        until = today + timedelta(days=days)
        kpis[f"warranty_expiring_{days}"] = qs.filter(warranty_end__range=(today, until)).count()
        kpis[f"amc_expiring_{days}"] = qs.filter(
            has_amc=True, amc_status="Active", amc_end__range=(today, until)).count()

    recent_transfers = TransferSerializer(
        AssetTransfer.objects.select_related('asset', 'new_owner', 'previous_owner')
        .order_by('-transfer_date')[:5], many=True).data
    open_checkouts = CheckoutSerializer(
        AssetCheckout.objects.filter(status="Open").select_related('asset', 'user')
        .order_by('-checkout_date')[:5], many=True).data
    expiring_assets = AssetSerializer(
        Asset.objects.filter(warranty_end__range=(today, soon))
        .order_by('warranty_end')[:5], many=True).data
    return Response({"kpis": kpis, "recent_transfers": recent_transfers,
                     "open_checkouts": open_checkouts, "expiring_assets": expiring_assets})


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


@api_view(['GET'])
def charts(request, name):
    if name == "category-distribution":
        rows = (Category.objects.annotate(n=Count('asset')).filter(n__gt=0)
                .values_list('category_name', 'n'))
        return Response({"labels": [r[0] for r in rows], "data": [r[1] for r in rows]})

    if name == "status-distribution":
        rows = Asset.objects.values('status').annotate(n=Count('id')).order_by()
        return Response({"labels": [r['status'] for r in rows],
                         "data": [r['n'] for r in rows]})

    if name == "department-usage":
        rows = (Department.objects.annotate(n=Count('asset')).values_list('name', 'n'))
        return Response({"labels": [r[0] for r in rows], "data": [r[1] for r in rows]})

    if name == "purchase-trend":
        labels, data = [], []
        for y, m in _last_12_months():
            start = date(y, m, 1)
            end = date(y + (m == 12), (m % 12) + 1, 1)
            total = (Asset.objects
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
                status="Approved").count()
            labels.append(start.strftime("%b %y"))
            data.append(count)
        return Response({"labels": labels, "data": data})

    if name == "warranty-timeline":
        today = date.today()
        buckets = [("Expired", None, None), ("0-30 days", 0, 30), ("31-60 days", 31, 60),
                   ("61-90 days", 61, 90), ("90+ days", 91, None)]
        labels, data = [], []
        for label, lo, hi in buckets:
            q = Asset.objects.filter(warranty_end__isnull=False)
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
            q = Asset.objects.filter(has_amc=True, amc_status="Active", amc_end__isnull=False)
            if label == "Expired":
                q = q.filter(amc_end__lt=today)
            else:
                q = q.filter(amc_end__gte=today + timedelta(days=lo))
                if hi is not None:
                    q = q.filter(amc_end__lte=today + timedelta(days=hi))
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
    return (["Asset ID", "Tag No", "Name", "Category", "Serial No", "Owner",
             "Department", "Location", "Status", "Value"], rows)


def _report_movement():
    rows = []
    for t in AssetTransfer.objects.select_related('asset', 'previous_owner', 'new_owner', 'approved_by').order_by('-transfer_date'):
        rows.append([f"TRF-{t.id:05d}", t.asset.asset_id, t.asset.name or "-",
                     t.previous_owner.user_name if t.previous_owner else "IT Store",
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
        rows.append([log.date.strftime("%d-%b-%Y %H:%M"), log.username, log.action,
                     log.module, log.old_value or "-", log.new_value or "-",
                     log.ip_address or "-"])
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
    for a in Asset.objects.filter(has_amc=True).select_related('category').order_by('amc_end'):
        days = a.amc_days_left
        status = "-"
        if a.amc_status == "Ended":
            status = "Ended"
        elif days is None:
            status = "Not set"
        else:
            status = "Expired" if days < 0 else f"{days} days left"
        rows.append([a.asset_id, a.name or "-",
                     a.category.category_name if a.category else "-",
                     a.amc_start.strftime("%d-%b-%Y") if a.amc_start else "-",
                     a.amc_end.strftime("%d-%b-%Y") if a.amc_end else "-",
                     a.amc_status, status])
    return (["Asset ID", "Name", "Category", "AMC Start", "AMC End", "AMC Status",
             "Expiry"], rows)


def _report_lost():
    rows = []
    for a in Asset.objects.filter(status="Lost").select_related('custodian', 'department').order_by('asset_id'):
        rows.append([a.asset_id, a.name or "-",
                     a.custodian.user_name if a.custodian else "-",
                     a.department.name if a.department else "-",
                     a.condition])
    return (["Asset ID", "Name", "Last Known Custodian", "Department", "Condition"], rows)


REPORTS = {
    "register": ("Asset Register Report", _report_register),
    "movement": ("Asset Movement Report", _report_movement),
    "warranty": ("Warranty Expiry Report", _report_warranty),
    "purchase": ("Purchase Report", _report_purchase),
    "employee": ("Employee Asset Report", _report_employee),
    "audit": ("Asset Audit Report", _report_audit),
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
                {"key": k, "title": title} for k, (title, _) in REPORTS.items()]})
        if key not in REPORTS:
            return Response({"detail": "Unknown report."}, status=http_status.HTTP_404_NOT_FOUND)
        title, fn = REPORTS[key]
        headers, rows = fn()
        return Response({"key": key, "title": title, "headers": headers, "rows": rows})


class ReportExportView(APIView):
    permission_classes = [HasRolePermission]
    required_permission = "report_access"

    def get(self, request, key, fmt):
        from django.http import FileResponse

        from core.exports import build_excel, build_table_pdf
        if key not in REPORTS or fmt not in ("pdf", "excel"):
            return Response({"detail": "Unknown report or format."},
                            status=http_status.HTTP_404_NOT_FOUND)
        title, fn = REPORTS[key]
        headers, rows = fn()
        company = Setting.get("company_name", "Cloud Shoe Factory")
        log_action(request, "Report Export", "Reports", new_value=f"{key} ({fmt})")
        if fmt == "pdf":
            buf = build_table_pdf(title, headers, rows, company_name=company)
            return FileResponse(buf, as_attachment=True, content_type='application/pdf',
                                filename=f"{key}_report.pdf")
        buf = build_excel(title, headers, rows, company_name=company)
        return FileResponse(
            buf, as_attachment=True,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=f"{key}_report.xlsx")

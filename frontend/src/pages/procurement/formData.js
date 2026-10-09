export const buildProcurementFormData = (payload, invoiceFile = null) => {
  const form = new FormData();

  Object.entries(payload).forEach(([key, value]) => {
    if (key === 'asset_ids') {
      value.forEach((assetId) => form.append(key, assetId));
    } else if (key === 'arrivals') {
      form.append(key, JSON.stringify(value));
    } else if (value !== null && value !== undefined) {
      form.append(key, value);
    }
  });

  if (invoiceFile) form.append('invoice_file', invoiceFile);
  return form;
};

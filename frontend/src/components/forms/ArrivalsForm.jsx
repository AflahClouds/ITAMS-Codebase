import { Alert, Box, Checkbox, FormControlLabel, Typography } from "@mui/material";
import InventoryIcon from "@mui/icons-material/Inventory";
import DateForm from "./DateForm";
import SelectForm from "./SelectForm";

/**
 * Arrival evidence for each Asset on a purchase, plus the operator's attestation.
 *
 * B6 FR-009 (decision C7) makes physical arrival a precondition the system enforces
 * rather than something it trusts was true because an invoice was typed. Every linked
 * Asset needs an arrival date and a Location, and the person saving has to say plainly
 * that the goods are here. The backend refuses the save without both, so this is not a
 * courtesy prompt — it is the only way the form can succeed.
 */
export default function ArrivalsForm({
  assets,
  selectedIds,
  locations,
  arrivals,
  attested,
  onArrivalChange,
  onAttestChange,
  showAttestError,
}) {
  const selected = assets.filter((asset) => selectedIds.includes(asset.id));

  if (selected.length === 0) {
    return (
      <Alert severity="info" sx={{ margin: "10px" }}>
        Select the assets this purchase covers, then record when and where each one
        arrived.
      </Alert>
    );
  }

  return (
    <Box sx={{ width: "100%", padding: "10px" }}>
      <Box className={"TopBar"} sx={{ marginBottom: "10px" }}>
        <InventoryIcon />
        <Typography
          sx={{ marginLeft: "10px", fontWeight: "bold" }}
          variant="subtitle2"
        >
          Arrival record — required for every asset on this purchase
        </Typography>
      </Box>

      {selected.map((asset) => {
        const arrival = arrivals[asset.id] || {};
        return (
          <Box
            key={asset.id}
            sx={{
              display: "flex",
              gap: "15px",
              alignItems: "flex-start",
              marginBottom: "15px",
              flexWrap: "wrap",
            }}
          >
            <Typography sx={{ minWidth: "140px", paddingTop: "15px" }} variant="body2">
              <strong>{asset.asset_id}</strong>
              {asset.name ? ` — ${asset.name}` : ""}
            </Typography>

            <Box sx={{ flex: "1 1 200px" }}>
              <DateForm
                label="Arrived on"
                name={`arrival_date_${asset.id}`}
                value={arrival.arrived_on || null}
                onChange={(newValue) =>
                  onArrivalChange(asset.id, "arrived_on", newValue)
                }
              />
            </Box>

            <Box sx={{ flex: "1 1 200px" }}>
              <SelectForm
                label="Arrived at"
                options={locations}
                labelKey="name"
                name={`arrival_location_${asset.id}`}
                value={arrival.location || ""}
                onChange={(event) =>
                  onArrivalChange(asset.id, "location", event.target.value)
                }
              />
            </Box>
          </Box>
        );
      })}

      <FormControlLabel
        control={
          <Checkbox
            checked={Boolean(attested)}
            onChange={(event) => onAttestChange(event.target.checked)}
            name="attested"
          />
        }
        label="I confirm the assets listed above have physically arrived."
      />
      {showAttestError && (
        <Alert severity="error" sx={{ marginTop: "10px" }}>
          Confirm the assets have arrived before saving this purchase.
        </Alert>
      )}
    </Box>
  );
}

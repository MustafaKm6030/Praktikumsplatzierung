import React, { useState, useEffect } from 'react';
import { 
    Dialog, DialogTitle, DialogContent, DialogActions, 
    Button, Select, MenuItem, FormControl, InputLabel, 
    Checkbox, FormControlLabel, Typography, Alert, Box 
} from '@mui/material';

const AdjustAssignmentDialog = ({ open, onClose, mentorId, onSaveSuccess }) => {
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState(null);
    const [selections, setSelections] = useState([]); 
    const [forceOverride, setForceOverride] = useState(false);
    const [error, setError] = useState(null);

    // 1. Fetch Data when Modal Opens
    useEffect(() => {
        if (open && mentorId) {
            setLoading(true);
            setError(null);
            // Fetch the eligibility data for this specific mentor
            fetch(`/api/pls/${mentorId}/adjustment_data/`)
                .then(res => {
                    if (!res.ok) throw new Error("Failed to load data");
                    return res.json();
                })
                .then(apiData => {
                    setData(apiData);
                    // Pre-fill selections: Create slots based on capacity
                    const current = apiData.current_assignments || [];
                    const slots = [];
                    for (let i = 0; i < apiData.capacity; i++) {
                        // Use existing assignment or empty placeholder
                        slots.push(current[i] || { practicum_type: '', subject_code: '' });
                    }
                    setSelections(slots);
                    setLoading(false);
                })
                .catch(err => {
                    setError("Could not load mentor data.");
                    setLoading(false);
                });
        }
    }, [open, mentorId]);

    // 2. Handle Dropdown Changes
    const handleSelectionChange = (index, valueString) => {
        const newSelections = [...selections];
        // We store the whole object in the value as a JSON string
        newSelections[index] = JSON.parse(valueString); 
        setSelections(newSelections);
    };

    // 3. Save Changes
    const handleSave = () => {
        const payload = {
            mentor_id: mentorId,
            force_override: forceOverride,
            // Remove empty slots before sending to backend
            proposed_assignments: selections.filter(s => s.practicum_type !== '')
        };

        fetch('/api/assignments/adjust/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(async res => {
            if (res.ok) {
                const updatedList = await res.json();
                onSaveSuccess(updatedList); // Callback to refresh the parent table
                onClose();
            } else {
                const errData = await res.json();
                setError(errData.message || "Failed to save assignments.");
            }
        })
        .catch(err => setError("Network error occurred."));
    };

    if (!open) return null;

    return (
        <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
            <DialogTitle>
                Adjust Assignments for {data ? data.mentor_name : 'Loading...'}
            </DialogTitle>
            
            <DialogContent dividers>
                {loading && <Typography>Loading data...</Typography>}
                
                {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

                {!loading && data && selections.map((selection, index) => (
                    <Box key={index} sx={{ mb: 3 }}>
                        <Typography variant="subtitle2" gutterBottom>Slot {index + 1}</Typography>
                        <FormControl fullWidth size="small">
                            <InputLabel id={`slot-label-${index}`}>Assignment</InputLabel>
                            <Select
                                labelId={`slot-label-${index}`}
                                label="Assignment"
                                value={JSON.stringify(selection)}
                                onChange={(e) => handleSelectionChange(index, e.target.value)}
                            >
                                {/* Option to clear the slot */}
                                <MenuItem value={JSON.stringify({ practicum_type: '', subject_code: '' })}>
                                    <em>(Empty / Unassigned)</em>
                                </MenuItem>
                                
                                {/* Legal options from backend */}
                                {data.all_eligibilities.map((option, i) => (
                                    <MenuItem key={i} value={JSON.stringify(option)}>
                                        {option.practicum_type} 
                                        {option.subject_code && option.subject_code !== 'N/A' 
                                            ? ` - ${option.subject_code}` 
                                            : ''}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </Box>
                ))}

                {!loading && data && (
                    <FormControlLabel
                        control={
                            <Checkbox 
                                checked={forceOverride} 
                                onChange={(e) => setForceOverride(e.target.checked)} 
                                color="error" 
                            />
                        }
                        label={
                            <Typography variant="body2" color="error">
                                Force Override (Ignore warnings like duplicate subjects)
                            </Typography>
                        }
                        sx={{ mt: 2 }}
                    />
                )}
            </DialogContent>

            <DialogActions>
                <Button onClick={onClose} color="inherit">Cancel</Button>
                <Button onClick={handleSave} variant="contained" color="primary">
                    Save Changes
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default AdjustAssignmentDialog;
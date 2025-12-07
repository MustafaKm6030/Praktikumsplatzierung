import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import Loader from '../ui/Loader';

// Fix default marker icon issue with React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Lower Bavaria center (Passau region)
const LOWER_BAVARIA_CENTER = [48.5665, 13.4318];
const DEFAULT_ZOOM = 9;

const MapView = ({ schools = [] }) => {
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const timer = setTimeout(() => setIsLoading(false), 1000);
        return () => clearTimeout(timer);
    }, []);

    if (isLoading) {
        return <Loader message="Karte wird geladen..." />;
    }

    return (
        <div style={{ height: '600px', width: '100%', borderRadius: '12px', overflow: 'hidden' }}>
            <MapContainer
                center={LOWER_BAVARIA_CENTER}
                zoom={DEFAULT_ZOOM}
                style={{ height: '100%', width: '100%' }}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {schools.map((school) => {
                    if (!school.latitude || !school.longitude) return null;

                    return (
                        <Marker
                            key={school.id}
                            position={[school.latitude, school.longitude]}
                        >
                            <Popup>
                                <div style={{ padding: '8px' }}>
                                    <strong>{school.name}</strong>
                                    <br />
                                    {school.city && <span>{school.city}</span>}
                                    {school.district && <span><br />Bezirk: {school.district}</span>}
                                    {school.type && <span><br />Typ: {school.type}</span>}
                                </div>
                            </Popup>
                        </Marker>
                    );
                })}
            </MapContainer>
        </div>
    );
};

export default MapView;
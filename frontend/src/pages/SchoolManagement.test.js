import React from 'react';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// --- SETUP DYNAMIC MOCK FOR HOOK ---
const MOCK_USE_SCHOOL_DATA = jest.fn();

jest.mock('../components/school_management/useSchoolData', () => ({
    __esModule: true,
    default: () => MOCK_USE_SCHOOL_DATA(),
}));

// --- MOCK THE MAP COMPONENT ---
jest.mock('../components/school_management/MapView', () => {
    return function dummyMap() {
        return <div data-testid="map-view-mock">Map Component Placeholder</div>;
    };
});

// --- MOCK API REQUESTS ---
jest.mock('../components/school_management/SchoolsApi', () => ({
    fetchSchools: jest.fn(),
    createSchool: jest.fn(),
    updateSchool: jest.fn(),
    deleteSchool: jest.fn(),
    exportSchoolsCSV: jest.fn(),
    importSchoolsCSV: jest.fn(),
}));

// --- IMPORTS ---
import SchoolManagement from './SchoolManagement';
import { 
    createSchool, 
    deleteSchool, 
    exportSchoolsCSV 
} from '../components/school_management/SchoolsApi';

// --- THE TEST SUITE ---
describe('SchoolManagement Page Integration', () => {
    
    const TEST_CITY = 'Passau';

    const defaultData = {
        schools: [
            { id: 1, name: 'Grundschule Passau', city: TEST_CITY, school_type: 'GS', district: 'Innstadt', zone: 1 },
            { id: 2, name: 'Mittelschule Nord', city: TEST_CITY, school_type: 'MS', district: 'Hacklberg', zone: 2 }
        ],
        filteredSchools: [
             { id: 1, name: 'Grundschule Passau', city: TEST_CITY, school_type: 'GS', district: 'Innstadt', zone: 1 },
             { id: 2, name: 'Mittelschule Nord', city: TEST_CITY, school_type: 'MS', district: 'Hacklberg', zone: 2 }
        ],
        loading: false,
        error: null,
        searchQuery: '',
        setSearchQuery: jest.fn(),
        selectedDistrict: 'all', 
        setSelectedDistrict: jest.fn(),
        selectedType: 'all',
        setSelectedType: jest.fn(),
        selectedZone: 'all',
        setSelectedZone: jest.fn(),
        districts: ['Innstadt', 'Hacklberg'],
        types: ['GS', 'MS'],
        zones: [1, 2],
        fetchSchools: jest.fn(),
    };

    // Reset mocks before every test
    beforeEach(() => {
        jest.clearAllMocks();
        MOCK_USE_SCHOOL_DATA.mockReturnValue(defaultData);
    });

    test('1. Renders the school list correctly', () => {
        render(<SchoolManagement />);
        expect(screen.getByText(/Neue Schule hinzufügen/i)).toBeInTheDocument();
        expect(screen.getByText('Grundschule Passau')).toBeInTheDocument();
    });

    test('2. Opens "Add School" dialog and submits form', async () => {
        render(<SchoolManagement />);

        const addButton = screen.getByText(/Neue Schule hinzufügen/i);
        userEvent.click(addButton);

        // Target inputs inside the Dialog
        const dialog = screen.getByRole('dialog');
        const nameInput = within(dialog).getByLabelText(/Schulname */i);
        const cityInput = within(dialog).getByLabelText(/Stadt */i);
        const districtInput = within(dialog).getByLabelText(/Bezirk */i);

        // Fill Form
        userEvent.type(nameInput, 'Test Schule');
        userEvent.type(cityInput, 'Test City');
        userEvent.type(districtInput, 'Test District');
        
        // Mock successful creation
        createSchool.mockResolvedValue({ id: 3, name: 'Test Schule' });

        // Click Save
        const saveButton = within(dialog).getByRole('button', { name: 'Speichern' });
        userEvent.click(saveButton);

        // Verify API Call
        await waitFor(() => {
            expect(createSchool).toHaveBeenCalled();
        });
        expect(await screen.findByText(/Schule erfolgreich gespeichert/i)).toBeInTheDocument();
    });

    test('3. Deletes a school after confirmation', async () => {
        render(<SchoolManagement />);

        // Mock browser confirm dialog
        jest.spyOn(window, 'confirm').mockImplementation(() => true);
        deleteSchool.mockResolvedValue({});

        // Find delete button
        const rows = screen.getAllByRole('row');
        const firstRowButtons = within(rows[1]).getAllByRole('button');
        const deleteBtn = firstRowButtons[firstRowButtons.length - 1];
        
        userEvent.click(deleteBtn);

        expect(window.confirm).toHaveBeenCalled();
        await waitFor(() => {
            expect(deleteSchool).toHaveBeenCalledWith(1);
        });
    });

    test('4. Triggers CSV Export', async () => {
        render(<SchoolManagement />);
        exportSchoolsCSV.mockResolvedValue({});

        const exportBtn = screen.getByText(/Exportieren/i);
        userEvent.click(exportBtn);

        await waitFor(() => {
            expect(exportSchoolsCSV).toHaveBeenCalledTimes(1);
        });
    });

    test('5. Displays Error State when API fails', async () => {
        // --- DYNAMIC MOCK ---
        // We override the default mock to return an error ONLY for this test
        MOCK_USE_SCHOOL_DATA.mockReturnValue({
            ...defaultData,
            loading: false,
            error: 'Backend Offline: 500 Error'
        });
        
        render(<SchoolManagement />);

        // We expect to see the Alert with the error message
        expect(await screen.findByText(/Backend Offline: 500 Error/i)).toBeInTheDocument();
        // We check that the table is NOT rendered (or at least the data isn't there)
        expect(screen.queryByText('Grundschule Passau')).not.toBeInTheDocument();
    });
});
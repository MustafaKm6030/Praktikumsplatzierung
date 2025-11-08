import React, { useEffect, useMemo, useState } from "react";
import "./PlManagementListPage.css";

const MOCK_PLS: Praktikumslehrkraft[] = [
    {
      id: 1,
      plId: "PL001",
      name: "Anna Schmidt",
      schule: "Grundschule Regen",
      schulart: "GS",
      hauptfach: "Deutsch",
      bevorzugtePraktika: ["PDP I", "SFP"],
      anrechnungsstd: 1,
      schulamt: "Regen",
      kapazitaetGesamt: 5,
      zugewieseneStudierende: 3,
    },
    {
      id: 2,
      plId: "PL002",
      name: "Michael Müller",
      schule: "Mittelschule Passau",
      schulart: "MS",
      hauptfach: "Mathematik",
      bevorzugtePraktika: ["PDP I", "PDP II", "ZSP"],
      anrechnungsstd: 2,
      schulamt: "Passau-Land",
      kapazitaetGesamt: 7,
      zugewieseneStudierende: 5,
    },
    {
      id: 3,
      plId: "PL003",
      name: "Sarah Weber",
      schule: "Grundschule Deggendorf",
      schulart: "GS",
      hauptfach: "Musik",
      bevorzugtePraktika: ["SFP", "ZSP"],
      anrechnungsstd: 1,
      schulamt: "Deggendorf",
      kapazitaetGesamt: 6,
      zugewieseneStudierende: 2,
    },
    {
      id: 4,
      plId: "PL004",
      name: "Thomas Bauer",
      schule: "Grund- und Mittelschule Straubing",
      schulart: "GS/MS",
      hauptfach: "Sport",
      bevorzugtePraktika: ["PDP I", "PDP II"],
      anrechnungsstd: 1,
      schulamt: "Straubing",
      kapazitaetGesamt: 8,
      zugewieseneStudierende: 4,
    },
    {
      id: 5,
      plId: "PL005",
      name: "Julia Fischer",
      schule: "Grundschule Landshut",
      schulart: "GS",
      hauptfach: "HSU",
      bevorzugtePraktika: ["PDP I", "SFP"],
      anrechnungsstd: 1,
      schulamt: "Landshut",
      kapazitaetGesamt: 6,
      zugewieseneStudierende: 3,
    },
  ];
  

type Praktikumslehrkraft = {
  id: number;

  plId: string;                     // e.g. "PL001"
  name: string;                     // "Anna Schmidt"
  schule: string;                   // "Grundschule Regen"
  schulart: string;                 // "GS", "MS", "GS/MS", ...
  hauptfach: string;                // "Deutsch", "Mathematik", ...
  bevorzugtePraktika: string[];     // ["PDP I", "SFP", "ZSP"]
  anrechnungsstd: number;           // 1, 2, ...
  schulamt: string;                 // "Regen", "Passau-Land", ...
  kapazitaetGesamt: number;         // 5, 7, ...
  zugewieseneStudierende: number;   // 3, 5, ...
};

const PlManagementListPage: React.FC = () => {
  const [pls, setPls] = useState<Praktikumslehrkraft[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState("");
  const [schulamtFilter, setSchulamtFilter] = useState<string>("all");
  const [schulartFilter, setSchulartFilter] = useState<string>("all");

  // =========================================================
  // 1. Fetch data from GET /api/pls
  // =========================================================
  useEffect(() => {
    let active = true;
  
    const load = async () => {
      setLoading(true);
      setError(null);
  
      try {
        // 🧩 Toggle this line when backend is not ready:
        // const useMock = true;   // <-- set true to use MOCK_PLS
        const useMock = true;     // <-- set false when backend works
  
        if (useMock) {
          console.log("Using mock PL data...");
          if (active) setPls(MOCK_PLS);
          return;
        }
  
        // 🧠 Fetch from backend
        const res = await fetch("/api/pls", {
          headers: {
            Accept: "application/json",
          },
        });
  
        if (!res.ok) {
          const text = await res.text();
          console.error("Backend error:", text);
          throw new Error(
            `Fehler beim Laden der PL-Daten. (${res.status} ${res.statusText})`
          );
        }
  
        const raw = await res.json();
  
        // ✅ Defensive: ensure it’s an array
        if (!Array.isArray(raw)) {
          console.error("Unexpected API response:", raw);
          throw new Error("Unerwartetes API-Format – erwartet ein Array.");
        }
  
        // 🧠 Map backend fields → our UI model
        const data: Praktikumslehrkraft[] = raw.map((item: any, idx: number) => ({
          id: item.id ?? idx,
          plId: item.plId ?? item.pl_id ?? "",
          name: item.name ?? "",
          schule: item.schule ?? item.school ?? "",
          schulart: item.schulart ?? item.schoolType ?? "",
          hauptfach: item.hauptfach ?? item.mainSubject ?? "",
          bevorzugtePraktika:
            item.bevorzugtePraktika ??
            item.preferredPraktika ??
            item.preferred_praktika ??
            [],
          anrechnungsstd: item.anrechnungsstd ?? item.creditHours ?? 0,
          schulamt: item.schulamt ?? item.schoolOffice ?? "",
          kapazitaetGesamt: item.kapazitaetGesamt ?? item.capacity_total ?? 0,
          zugewieseneStudierende:
            item.zugewieseneStudierende ?? item.assigned_students ?? 0,
        }));
  
        if (active) {
          setPls(data);
          console.log("Loaded PLs:", data);
        }
      } catch (e: unknown) {
        console.error("❌ Error loading PL data:", e);
        const message =
          e instanceof Error ? e.message : "Unbekannter Fehler beim Laden der Daten.";
        if (active) setError(message);
      } finally {
        if (active) setLoading(false);
      }
    };
  
    load();
  
    // Cleanup flag in case component unmounts
    return () => {
      active = false;
    };
  }, []);
  

  // =========================================================
  // 2. Distinct filter options
  // =========================================================
  const schulamtOptions = useMemo(
    () =>
      Array.from(new Set(pls.map((pl) => pl.schulamt))).sort((a, b) =>
        a.localeCompare(b, "de-DE")
      ),
    [pls]
  );

  const schulartOptions = useMemo(
    () =>
      Array.from(new Set(pls.map((pl) => pl.schulart))).sort((a, b) =>
        a.localeCompare(b, "de-DE")
      ),
    [pls]
  );

  // =========================================================
  // 3. Search + filters
  // =========================================================
  const filteredPls = useMemo(() => {
    const term = search.trim().toLowerCase();

    return pls.filter((pl) => {
      const matchesSearch =
        term.length === 0 ||
        pl.plId.toLowerCase().includes(term) ||
        pl.name.toLowerCase().includes(term) ||
        pl.schule.toLowerCase().includes(term);

      const matchesSchulamt =
        schulamtFilter === "all" || pl.schulamt === schulamtFilter;

      const matchesSchulart =
        schulartFilter === "all" || pl.schulart === schulartFilter;

      return matchesSearch && matchesSchulamt && matchesSchulart;
    });
  }, [pls, search, schulamtFilter, schulartFilter]);

  // =========================================================
  // 4. Summary values (bottom text)
  // =========================================================
  const totalPlCount = pls.length;
  const totalAvailableCapacity = useMemo(
    () =>
      pls.reduce((sum, pl) => {
        const free =
          pl.kapazitaetGesamt - pl.zugewieseneStudierende > 0
            ? pl.kapazitaetGesamt - pl.zugewieseneStudierende
            : 0;
        return sum + free;
      }, 0),
    [pls]
  );

  const formatCapacityCell = (pl: Praktikumslehrkraft) => {
    const free =
      pl.kapazitaetGesamt - pl.zugewieseneStudierende > 0
        ? pl.kapazitaetGesamt - pl.zugewieseneStudierende
        : 0;
    // e.g. "2 verfügbar"
    return `${free} verfügbar`;
  };

  const formatAssignedCell = (pl: Praktikumslehrkraft) =>
    `${pl.zugewieseneStudierende} / ${pl.kapazitaetGesamt}`;

  // =========================================================
  // 5. Render
  // =========================================================
  return (
    <div className="pl-page">
      {/* Header + Add button, like the mockup */}
      <header className="pl-page__header">
        <div>
          <h1 className="pl-page__title">Praktikumslehrkräfte Verwaltung</h1>
          <p className="pl-page__subtitle">
            Verwalten Sie PL Profile, Fachqualifikationen und Verfügbarkeiten
          </p>
        </div>

        <button
          type="button"
          className="pl-page__add-button"
          onClick={() => {
            // later: navigate to a "new PL" form
            // e.g. navigate("/pls/new") if you use react-router
            console.log("Neue PL hinzufügen");
          }}
        >
          + Neue PL hinzufügen
        </button>
      </header>

      {/* Search bar + filters row */}
      <section className="pl-page__filters">
        <div className="pl-page__search-wrapper">
          <span className="pl-page__search-icon" aria-hidden="true">
            🔍
          </span>
          <input
            type="text"
            placeholder="Suche nach Name, Schule oder PL ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-page__search-input"
          />
        </div>

        <div className="pl-page__filter-selects">
          <select
            value={schulamtFilter}
            onChange={(e) => setSchulamtFilter(e.target.value)}
            className="pl-page__select"
          >
            <option value="all">Alle Schulämter</option>
            {schulamtOptions.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>

          <select
            value={schulartFilter}
            onChange={(e) => setSchulartFilter(e.target.value)}
            className="pl-page__select"
          >
            <option value="all">Alle Schularten</option>
            {schulartOptions.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
        </div>
      </section>

      {/* Table box */}
      <section className="pl-page__table-wrapper">
        {loading && <div className="pl-page__info">Lade Daten…</div>}
        {error && (
          <div className="pl-page__error">
            Fehler: {error}
          </div>
        )}

        {!loading && !error && (
          <>
            <table className="pl-page__table">
              <thead>
                <tr>
                  <th>PL ID</th>
                  <th>Name</th>
                  <th>Schule</th>
                  <th>Schulart</th>
                  <th>Hauptfach</th>
                  <th>Bevorzugte Praktika</th>
                  <th>Anrechnungsstd.</th>
                  <th>Schulamt</th>
                  <th>Kapazität</th>
                  <th>Zugewiesene Studierende</th>
                </tr>
              </thead>
              <tbody>
                {filteredPls.map((pl) => (
                  <tr key={pl.id}>
                    <td>{pl.plId}</td>
                    <td>{pl.name}</td>
                    <td>{pl.schule}</td>
                    <td>{pl.schulart}</td>
                    <td>{pl.hauptfach}</td>
                    <td>
                      <div className="pl-page__chips">
                        {pl.bevorzugtePraktika.map((p) => (
                          <span key={p} className="pl-page__chip">
                            {p}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td>{pl.anrechnungsstd}</td>
                    <td>
                      <span className="pl-page__schulamt-pill">
                        {pl.schulamt}
                      </span>
                    </td>
                    <td>
                      <span className="pl-page__capacity-pill">
                        {formatCapacityCell(pl)}
                      </span>
                    </td>
                    <td>{formatAssignedCell(pl)}</td>
                  </tr>
                ))}

                {filteredPls.length === 0 && (
                  <tr>
                    <td colSpan={10} className="pl-page__empty">
                      Keine Praktikumslehrkräfte gefunden.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>

            {/* Footer row like in the screenshot */}
            <div className="pl-page__footer">
              <div>Gesamt: {totalPlCount} Praktikumslehrkräfte</div>
              <div>Verfügbare Kapazität: {totalAvailableCapacity} Plätze</div>
            </div>
          </>
        )}
      </section>
    </div>
  );
};

export default PlManagementListPage;
   
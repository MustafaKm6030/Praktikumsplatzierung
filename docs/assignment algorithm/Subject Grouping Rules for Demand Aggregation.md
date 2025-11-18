Official Subject Grouping Rules for Demand Aggregation (Issue #5 & #8)
Purpose: These rules are used to administratively consolidate the raw subject choices of students into the official planning categories used by the Praktikumsamt. This logic applies only to SFP and ZSP internships.
Source of Truth: These rules are derived directly from the official Bedarfsermittlung (Demand Assessment) documents provided for the Schuljahr 2025/26. They are authoritative for this project.
Default Behavior: If a student's subject is not explicitly listed in a mapping rule below, its original name should be used as the demand category.

1. Grundschule (GS) Rules
For ZSP Internships (WiSe 2025/26)
| If Raw Student Subject is... | Map to this Demand Category...
 | | :--------------------------- | :----------------------------- | |
 Geschichte, Geographie, Sozialkunde, Biologie, Chemie and Physik  | Heimat- und Sachunterricht (HSU) | 
| Deutsch als Zweitsprache | Deutsch als Zweitsprache (DaZ) | 
| Kath. Religion or Evang. Religion | Kath. Religion (KRel) |
 | Deutsch | Deutsch (D) | 
| Englisch | Englisch (E) |
 | Kunsterziehung | Kunsterziehung (KE) |
 | Mathematik | Mathematik (MA) | 
| Musik | Musik (MU) | 
| Sport | Sport (SP) | 
| Schriftspracherwerb | Schriftspracherwerb (SSE) | 

For SFP Internships (SoSe 2026)

| If Raw Student Subject is... | Map to this Demand Category... |
 | :--------------------------- | :----------------------------- | 
| Sozialkunde, Politik | Sozialkunde (SK), Politik und Gesellschaft (PUG) | 
| Deutsch als Zweitsprache | Deutsch als Zweitsprache (DaZ) | 
| Kath. Religion or Evang. Religion | Kath. Religion (KRel) | 
| Deutsch | Deutsch (D) | 
| Englisch | Englisch (E) |
 | Geschichte | Geschichte | 
| Geographie | Geographie |
 | Kunsterziehung | Kunsterziehung (KE) |
 | Mathematik | Mathematik (MA) |

2. Mittelschule (MS) Rules
(These rules apply to both SFP and ZSP internships as the demand categories are consistent across the provided documents.)

| If Raw Student Subject is... | Map to this Demand Category... |
| :--------------------------- | :----------------------------- |
| Arbeitslehre, Wirtschaft, Berufskunde | Arbeitslehre (AL), Wirtschaft und Beruf (WIB) |
| Sozialkunde, Politik         | Sozialkunde (SK), Politik und Gesellschaft (PUG) |
| Deutsch als Zweitsprache     | Deutsch als Zweitsprache (DaZ) |
| Kath. Religion or Evang. Religion | Kath. Religion (KRel) |
| Deutsch                      | Deutsch (D) |
| Englisch                     | Englisch (E) |
| Geographie                   | Geographie (GEO) |
| Geschichte                   | Geschichte (GE) |
| Informatik                   | Informatik (I) |
| Kunsterziehung               | Kunsterziehung (KE) |
| Mathematik                   | Mathematik (MA) |
| Musik                        | Musik (MU) |
| Sport                        | Sport (SP) |

Recommended Implementation: subject_grouping_rules.json
To ensure these rules are maintainable, they should be stored in a configuration file like the one below, not hard-coded.
codeJSON
{
  "GS": {
    "ZSP": {
      "Geschichte": "Heimat- und Sachunterricht (HSU)",
      "Geographie": "Heimat- und Sachunterricht (HSU)",
      "Sozialkunde": "Heimat- und Sachunterricht (HSU)",
      "Biologie": "Heimat- und Sachunterricht (HSU)",
      "Chemie": "Heimat- und Sachunterricht (HSU)",
      "Physik": "Heimat- und Sachunterricht (HSU)",
      "Deutsch als Zweitsprache": "Deutsch als Zweitsprache (DaZ)",
      "Kath. Religion": "Kath. Religion (KRel)",
      "Evang. Religion": "Kath. Religion (KRel)"
    },
    "SFP": {
      "Sozialkunde": "Sozialkunde (SK), Politik und Gesellschaft (PUG)",
      "Politik": "Sozialkunde (SK), Politik und Gesellschaft (PUG)",
      "Deutsch als Zweitsprache": "Deutsch als Zweitsprache (DaZ)",
      "Kath. Religion": "Kath. Religion (KRel)",
      "Evang. Religion": "Kath. Religion (KRel)"
    }
  },
  "MS": {
    "ZSP": {
      "Arbeitslehre": "Arbeitslehre (AL), Wirtschaft und Beruf (WIB)",
      "Wirtschaft": "Arbeitslehre (AL), Wirtschaft und Beruf (WIB)",
      "Berufskunde": "Arbeitslehre (AL), Wirtschaft und Beruf (WIB)",
      "Sozialkunde": "Sozialkunde (SK), Politik und Gesellschaft (PUG)",
      "Politik": "Sozialkunde (SK), Politik und Gesellschaft (PUG)",
      "Kath. Religion": "Kath. Religion (KRel)",
      "Evang. Religion": "Kath. Religion (KRel)"
    },
    "SFP": {
      "Arbeitslehre": "Arbeitslehre (AL), Wirtschaft und Beruf (WIB)",
      "Wirtschaft": "Arbeitslehre (AL), Wirtschaft und Beruf (WIB)",
      "Berufskunde": "Arbeitslehre (AL), Wirtschaft und Beruf (WIB)",
      "Sozialkunde": "Sozialkunde (SK), Politik und Gesellschaft (PUG)",
      "Politik": "Sozialkunde (SK), Politik und Gesellschaft (PUG)",
      "Kath. Religion": "Kath. Religion (KRel)",
      "Evang. Religion": "Kath. Religion (KRel)"
    }
  }
}


## Minimalny exporter IOC z MISP (Docker + Python)

### Zmienne środowiskowe

- **MISP_URL**: URL instancji MISP, np. `https://misp.example.com`
- **MISP_API_KEY**: klucz API użytkownika w MISP
- **MISP_VERIFY_SSL**: `true`/`false` (domyślnie `true`)
- **MISP_TAGS**: lista tagów, po których filtrujemy eventy, np. `tlp:white,osint`
- **OUTPUT_PATH**: ścieżka pliku wyjściowego z IOC  
  - domyślnie `/data/iocs.json` dla `OUTPUT_FORMAT=json`  
  - domyślnie `/data/iocs.edl` dla `OUTPUT_FORMAT=edl`
- **OUTPUT_FORMAT**: `json` (domyślnie) lub `edl` (lista IOC po jednym na linię, np. pod NGFW)

### Budowanie obrazu

```bash
docker build -t misp-ioc-exporter .
```

### Uruchomienie

```bash
docker run --rm \
  -e MISP_URL="https://misp.example.com" \
  -e MISP_API_KEY="YOUR_KEY" \
  -e MISP_VERIFY_SSL="true" \
  -e MISP_TAGS="tlp:white,osint" \
  -e OUTPUT_FORMAT="json" \
  -v "$(pwd)/data:/data" \
  misp-ioc-exporter
```

Plik z IOC pojawi się w katalogu `data` na hoście.  
Przy `OUTPUT_FORMAT=edl` domyślną nazwą będzie `iocs.edl` – płaska lista wartości (jeden IOC na linię), gotowa np. do wczytania jako EDL w NGFW.

### Licencja

MIT License – zobacz plik [LICENSE](LICENSE).


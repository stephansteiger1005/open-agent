# API Usage Examples

## Base URL
```
http://localhost:8080
```

## Swagger UI
Access the interactive API documentation at:
```
http://localhost:8080/swagger-ui.html
```

## Health Check
```bash
curl http://localhost:8080/actuator/health
```

## Data Format Information

**Important**: The PLMXML data is stored in the database in **zlib-compressed format**.

The API handles compression/decompression automatically:
- **Input (POST)**: Your Base64-encoded PLMXML → API decodes Base64 → API compresses with zlib → Stored in DB
- **Output (GET)**: DB retrieves compressed data → API decompresses with zlib → Returned as raw XML file for download

From the client perspective:
- **POST**: You send Base64-encoded PLMXML strings
- **GET**: You receive the decompressed PLMXML as a downloadable XML file

The zlib compression is transparent.

## Complete MIDGUARD Schema

The PartInfo table follows the complete MIDGUARD schema with composite key (sachnummer, revision, sequenz):

- `obsoleteEntry` (SMALLINT) - Optional obsolete flag
- `clazz` (VARCHAR(16)) - Required part class
- `sachnummer` (VARCHAR(32)) - Required part number (part of primary key)
- `revision` (INTEGER) - Required revision number (part of primary key)
- `sequenz` (INTEGER) - Required sequence number (part of primary key)
- `owner` (VARCHAR(32)) - Optional owner
- `status` (VARCHAR(16)) - Optional status
- `frozen` (SMALLINT) - Optional frozen flag
- `nomenclature` (VARCHAR(256)) - Optional part description
- `changeDescription` (VARCHAR(256)) - Optional change description
- `checksum3D` (BIGINT) - Optional 3D checksum
- `checksum2D` (BIGINT) - Optional 2D checksum
- `checksumBOM` (BIGINT) - Optional BOM checksum
- `plmxml` (BLOB) - PLMXML content (zlib-compressed)

## Example 1: Create a new PartInfo

```bash
curl -X POST http://localhost:8080/api/partinfo \
  -H "Content-Type: application/json" \
  -d '{
    "obsoleteEntry": 0,
    "clazz": "Part",
    "sachnummer": "PART-12345",
    "revision": 1,
    "sequenz": 1,
    "owner": "Engineering",
    "status": "Active",
    "frozen": 0,
    "nomenclature": "Test Part Assembly",
    "changeDescription": "Initial creation",
    "checksum3D": 123456789,
    "checksum2D": 987654321,
    "checksumBOM": 456789123,
    "plmxml": "PFBMTVhNTD48UGFydCBpZD0iMTIzNDUiIG5hbWU9IlRlc3QgUGFydCI+PFByb3BlcnR5IG5hbWU9Im1hdGVyaWFsIj5TdGVlbDwvUHJvcGVydHk+PC9QYXJ0PjwvUExNWE1MPg=="
  }'
```

The `plmxml` field contains Base64-encoded XML data. Decoded, it represents:
```xml
<PLMXML><Part id="12345" name="Test Part"><Property name="material">Steel</Property></Part></PLMXML>
```

**Note**: The API will automatically compress this data using zlib before storing it in the database.

**Response:**
```json
{
  "obsoleteEntry": 0,
  "clazz": "Part",
  "sachnummer": "PART-12345",
  "revision": 1,
  "sequenz": 1,
  "owner": "Engineering",
  "status": "Active",
  "frozen": 0,
  "nomenclature": "Test Part Assembly",
  "changeDescription": "Initial creation",
  "checksum3D": 123456789,
  "checksum2D": 987654321,
  "checksumBOM": 456789123,
  "plmxml": "PFBMTVhNTD48UGFydCBpZD0iMTIzNDUiIG5hbWU9IlRlc3QgUGFydCI+PFByb3BlcnR5IG5hbWU9Im1hdGVyaWFsIj5TdGVlbDwvUHJvcGVydHk+PC9QYXJ0PjwvUExNWE1MPg=="
}
```

## Example 2: Download Latest PLMXML by Sachnummer

This endpoint downloads the PLMXML file for the version with the highest revision and sequenz for the given sachnummer.

```bash
curl http://localhost:8080/api/partinfo/PART-12345 -o PART-12345_2_3.plmxml
```

or to view the content:

```bash
curl http://localhost:8080/api/partinfo/PART-12345
```

**Response (200 OK):**
- **Content-Type**: `application/xml`
- **Content-Disposition**: `form-data; name="attachment"; filename="PART-12345_2_3.plmxml"`
- **Body**: Decompressed PLMXML content (raw XML file)

Example PLMXML content:
```xml
<PLMXML><Part id="12345" name="Test Part"><Property name="material">Steel</Property></Part></PLMXML>
```

**Response (404 Not Found):**
```
(empty response body)
```

## Example 3: Download PLMXML by composite key

This endpoint downloads a specific PLMXML file by its complete composite key.

```bash
curl http://localhost:8080/api/partinfo/PART-12345/1/1 -o PART-12345_1_1.plmxml
```

or to view the content:

```bash
curl http://localhost:8080/api/partinfo/PART-12345/1/1
```

**Response (200 OK):**
- **Content-Type**: `application/xml`
- **Content-Disposition**: `form-data; name="attachment"; filename="PART-12345_1_1.plmxml"`
- **Body**: Decompressed PLMXML content (raw XML file)

Example PLMXML content:
```xml
<PLMXML><Part id="12345" name="Test Part"><Property name="material">Steel</Property></Part></PLMXML>
```

**Response (404 Not Found):**
```
(empty response body)
```

## Example 4: Update existing PartInfo

```bash
curl -X POST http://localhost:8080/api/partinfo \
  -H "Content-Type: application/json" \
  -d '{
    "obsoleteEntry": 0,
    "clazz": "Part",
    "sachnummer": "PART-12345",
    "revision": 1,
    "sequenz": 1,
    "owner": "Engineering",
    "status": "Updated",
    "frozen": 0,
    "nomenclature": "Updated Part Assembly",
    "changeDescription": "Updated with new features",
    "checksum3D": 123456789,
    "checksum2D": 987654322,
    "checksumBOM": 456789124,
    "plmxml": "PFBMTVhNTD48UGFydCBpZD0iMTIzNDUiIG5hbWU9IlVwZGF0ZWQgUGFydCI+PFByb3BlcnR5IG5hbWU9Im1hdGVyaWFsIj5BbHVtaW51bTwvUHJvcGVydHk+PC9QYXJ0PjwvUExNWE1MPg=="
  }'
```

**Response (200 OK):**
```json
{
  "obsoleteEntry": 0,
  "clazz": "Part",
  "sachnummer": "PART-12345",
  "revision": 1,
  "sequenz": 1,
  "owner": "Engineering",
  "status": "Updated",
  "frozen": 0,
  "nomenclature": "Updated Part Assembly",
  "changeDescription": "Updated with new features",
  "checksum3D": 123456789,
  "checksum2D": 987654322,
  "checksumBOM": 456789124,
  "plmxml": "PFBMTVhNTD48UGFydCBpZD0iMTIzNDUiIG5hbWU9IlVwZGF0ZWQgUGFydCI+PFByb3BlcnR5IG5hbWU9Im1hdGVyaWFsIj5BbHVtaW51bTwvUHJvcGVydHk+PC9QYXJ0PjwvUExNWE1MPg=="
}
```

## Example 5: Delete PartInfo

```bash
curl -X DELETE http://localhost:8080/api/partinfo/PART-12345/1/1
```

**Response (204 No Content):**
```
(empty response body)
```

**Response (404 Not Found):**
```
(empty response body when SNR does not exist)
```

## Example 5: Base64 Encoding/Decoding PLMXML

### Encode PLMXML to Base64 (for API requests):

**Linux/macOS:**
```bash
echo '<PLMXML><Part id="12345">Test</Part></PLMXML>' | base64
```

**PowerShell:**
```powershell
[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('<PLMXML><Part id="12345">Test</Part></PLMXML>'))
```

### Decode Base64 to PLMXML (from API responses):

**Linux/macOS:**
```bash
echo 'PFBMTVhNTD48UGFydCBpZD0iMTIzNDUiPlRlc3Q8L1BhcnQ+PC9QTE1YTUw+' | base64 -d
```

**PowerShell:**
```powershell
[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('PFBMTVhNTD48UGFydCBpZD0iMTIzNDUiPlRlc3Q8L1BhcnQ+PC9QTE1YTUw+'))
```

## Error Responses

### 400 Bad Request (Validation Error):

```bash
curl -X POST http://localhost:8080/api/partinfo \
  -H "Content-Type: application/json" \
  -d '{
    "snr": "",
    "plmxml": ""
  }'
```

**Response:**
```json
{
  "timestamp": "2026-01-12T16:54:26.543Z",
  "status": 400,
  "errors": {
    "plmxml": "PLMXML content is required",
    "snr": "Sachnummer (SNR) is required"
  },
  "message": "Validation failed"
}
```

## Integration with Other Tools

### Using with HTTPie

```bash
# Install HTTPie: https://httpie.io/
http POST http://localhost:8080/api/partinfo \
  snr="PART-001" \
  revision="A" \
  sequence="001" \
  plmxml="PFBMTVhNTD5UZXN0PC9QTE1YTUw+"
```

### Using with Postman

1. Import the OpenAPI specification from `http://localhost:8080/api-docs`
2. Or manually create requests using the examples above
3. Set Content-Type header to `application/json`

### Using with JavaScript/TypeScript

```javascript
const createPartInfo = async (snr, revision, sequence, plmxmlContent) => {
  // Encode PLMXML to Base64
  const plmxml = btoa(plmxmlContent);
  
  const response = await fetch('http://localhost:8080/api/partinfo', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ snr, revision, sequence, plmxml }),
  });
  
  return await response.json();
};

// Usage
const result = await createPartInfo(
  'PART-001',
  'A',
  '001',
  '<PLMXML><Part id="001">Test</Part></PLMXML>'
);
console.log(result);
```

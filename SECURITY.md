# Security

Report security issues privately to mohammed.zaton2@gmail.com using synthetic examples.
The program processes local files and makes no network requests. Never commit real
customer CSV files or secrets. The optional `--safe-excel` mode prefixes cells that
start with =, +, - or @, including negative numbers. Spreadsheet programs differ;
review exports and import untrusted columns as text. This mode is not a guarantee
against all spreadsheet execution behavior. Output can contain sensitive source data.

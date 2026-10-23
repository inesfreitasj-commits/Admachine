# Cosmetic bag infographics: German to English (Mei & Lily Singapore)

Done on 2026-10-23 in the Shopify store, collection "Cosmetic Bags" (250 products).

## What changed
Each product's three infographic images (media slots 2, 3 and 4) were replaced in place,
so order, other photos and URLs of the products are unchanged:

| Infographic | File name pattern | English version |
|---|---|---|
| Size chart | `catalogo-2-infografico-tamanhos-de_*` | https://d8j0ntlcm91z4.cloudfront.net/user_3BPQ4DNAuUfrHIUCx6eWutoRzXw/hf_20261023_141209_d0b1cb52-dc4c-48a7-814a-462e21fa5ad4.png |
| Care instructions | `catalogo-2-infografico-cuidados-de_*` | https://d8j0ntlcm91z4.cloudfront.net/user_3BPQ4DNAuUfrHIUCx6eWutoRzXw/hf_20261023_141208_d1579ea5-6691-4d29-8f1d-4b370e1a2e30.png |
| Features | `catalogo-2-infografico-caracteristicas-de_*` | https://d8j0ntlcm91z4.cloudfront.net/user_3BPQ4DNAuUfrHIUCx6eWutoRzXw/hf_20261023_141209_19bd97b6-bc7c-41a7-9d1a-e84bcebc8311.png |

750 files updated (250 per type), no errors. Checks after the update: no matching file left
un-updated, and no other file in the store was changed.

## Restoring the German originals
The original German images are stored in the Higgsfield media library (original 1254x1254 files):

| Infographic | Higgsfield media id | URL |
|---|---|---|
| Size chart | fcdd7043-6cce-4a04-b21a-88eaf38cb78f | https://d2ol7oe51mr4n9.cloudfront.net/user_3BPQ4DNAuUfrHIUCx6eWutoRzXw/fcdd7043-6cce-4a04-b21a-88eaf38cb78f.png |
| Care instructions | c20d2e25-5859-4084-a8bb-79fb60b7e165 | https://d2ol7oe51mr4n9.cloudfront.net/user_3BPQ4DNAuUfrHIUCx6eWutoRzXw/c20d2e25-5859-4084-a8bb-79fb60b7e165.png |
| Features | 5e57de8e-45ca-4849-9109-b1a202854527 | https://d2ol7oe51mr4n9.cloudfront.net/user_3BPQ4DNAuUfrHIUCx6eWutoRzXw/5e57de8e-45ca-4849-9109-b1a202854527.png |

To restore, run Shopify `fileUpdate` with `originalSource` set to the URL above on the files
matching each file name pattern.

# VIAL Brasilis — site vialbrasilis.it

Site estático publicado pelo GitHub Pages a partir da raiz do branch `main`.

## Estrutura

| Caminho | O que é |
|---|---|
| `index.html`, `en/`, `pt/` | Home em italiano, inglês e português (BR). **Gerados.** |
| `brasile/`, `pt/brasil/` | Página Itália–Brasil (IT e PT-BR). **Gerada.** |
| `privacy/`, `cookie/` | Informativa Privacy e Cookie Policy (IT). **Geradas.** |
| `sitemap.xml`, `robots.txt`, `CNAME` | SEO e domínio. `sitemap.xml` e `robots.txt` são gerados. |
| `css/`, `fonts/`, `img/` | Estilos, fontes hospedadas localmente e logo. |
| `src/` | **Fonte editável**: `template.html` (home) e `*.body.html` (demais páginas). |
| `tools/build.py` | Gerador das páginas. |

## Como editar o site

1. Edite os arquivos em `src/` (nunca os HTML gerados na raiz).
2. Rode `python tools/build.py` (requer `beautifulsoup4`).
3. Revise com `git diff`, faça commit e só então publique (push no `main`).

Convenções: `LASTMOD` em `tools/build.py` é a data usada no sitemap (atualize ao publicar); o link do CSS leva `?v=...` (troque o número em `src/template.html`, `src/traduzione.template.html` e `tools/build.py` quando o CSS mudar, para furar o cache do navegador).

## Projetos relacionados

O diagnóstico em si (a ferramenta e o material comercial) é **privado** e fica em outro projeto, fora deste repositório. As páginas de diagnóstico deste site (`src/diagnosi.*.body.html`) descrevem recursos dessa ferramenta: ao alterá-la, revise esses textos; e ao alterar os textos, confira se continuam verdadeiros.

## Material interno

Documentos de negócio e apresentações ficam **fora do repositório**, em `C:\vialbrasilis_interno\`
(`01_Negocio`, `02_Marketing_e_Apresentacoes`). Tudo o que está neste repositório é público.

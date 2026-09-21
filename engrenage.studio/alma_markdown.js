/*

Gestion legere d'un affichage markdown.

Sinon on pourrait aussi utiliser marked ou markdown-it.


(c) A.Mazel, sept 2026

Currently implemented:

- # Titres
-  ## Sous-titres jusqu'a ######
-  paragraphes
-  retours a la ligne
-  gras
-  italique
-  gras italique
-  barre
-  code inline
-  blocs de code avec ```
-  listes -, *, +
-  listes numerotees
-  liens HTTP/HTTPS
-  citations >
-  tableaux
-  separateurs ---
- images


-  echappement du HTML
-  protection contre les URL javascript

Don't handle:
-  les listes imbriquees, les cellules de tableaux complexes, les references, les footnotes
*/

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function safeUrl(url) {
    url = url.trim();

    // On n'autorise que HTTP(S)
    if (/^https?:\/\//i.test(url)) {
        return escapeHtml(url);
    }

    return "#";
}

function safeImageUrl(url) {
    try {
        const parsed = new URL(url, window.location.href);

        if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
            return "";
        }

        return parsed.href;
    } catch {
        return "";
    }
}


function inlineMarkdown(text) {
    
    // on gere les images en premier car elles contiennent des liens:
    
    let images = [];

    text = text.replace(
        /!\[([^\]]*)\]\((https?:\/\/[^)\s]+)\)(?:\{(\d+)(?:x(\d+))?\})?/gi,
        (_, alt, url, width, height) => {
            const token = `@@IMAGE_${images.length}@@`;

            let size = "";

            if (width) {
                size += ` width="${width}"`;
            }

            if (height) {
                size += ` height="${height}"`;
            }

            images.push(
                `<img src="${safeImageUrl(url)}" alt="${escapeHtml(alt)}" loading="lazy"${size}>`
            );

            return token;
        }
    );

    // IMPORTANT :
    // On echappe d'abord tout HTML fourni par l'utilisateur.
    text = escapeHtml(text);
        
    /*
     * Couleurs personnalisées
     *
     * {red|Texte rouge}
     * {green|Texte vert}
     * {#ff8800|Texte orange}
     */
    text = text.replace(
        /\{(red|green|blue|orange|purple|yellow|#[0-9a-fA-F]{3,6})\|([^{}]+)\}/g,
        (_, color, content) => {
            return `<span style="color:${color}">${content}</span>`;
        }
    );


    

    text = text.replace(
        /\{checked\}/g,
        '<span class="md-check">☑</span>'
    );

    text = text.replace(
        /\{check\}/g,
        '<span class="md-check">☐</span>'
    );


    // Code inline : `quelque chose`
    const code = [];

    text = text.replace(/`([^`]+)`/g, (_, value) => {
        const id = code.length;
        code.push("<code>" + value + "</code>");
        return `@@CODE${id}@@`;
    });


    // Liens
    text = text.replace(
        /\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/gi,
        (_, label, url) =>
            `<a href="${safeUrl(url)}" target="_blank" rel="noopener noreferrer">${label}</a>`
    );

    // Gras + italique
    text = text.replace(
        /\*\*\*(.+?)\*\*\*/g,
        "<strong><em>$1</em></strong>"
    );

    text = text.replace(
        /___(.+?)___/g,
        "<strong><em>$1</em></strong>"
    );

    // Gras
    text = text.replace(
        /\*\*(.+?)\*\*/g,
        "<strong>$1</strong>"
    );

    text = text.replace(
        /__(.+?)__/g,
        "<strong>$1</strong>"
    );

    // Italique
    text = text.replace(
        /(?<!\*)\*([^*\n]+)\*(?!\*)/g,
        "<em>$1</em>"
    );

    text = text.replace(
        /(?<!_)_([^_\n]+)_(?!_)/g,
        "<em>$1</em>"
    );

    // Barre
    text = text.replace(
        /~~(.+?)~~/g,
        "<del>$1</del>"
    );

    // Restaurer le code inline
    text = text.replace(
        /@@CODE(\d+)@@/g,
        (_, id) => code[Number(id)]
    );
    
    // Restaurer les images:
    text = text.replace(
        /@@IMAGE_(\d+)@@/g,
        (_, index) => images[Number(index)]
    );

    return text;
}


function isTableSeparator(line) {
    return /^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$/.test(line);
}


function parseTable(lines, start) {
    const header = lines[start];
    const separator = lines[start + 1];

    if (!separator || !isTableSeparator(separator)) {
        return null;
    }

    function splitRow(row) {
        row = row.trim();

        if (row.startsWith("|")) {
            row = row.slice(1);
        }

        if (row.endsWith("|")) {
            row = row.slice(0, -1);
        }

        return row.split("|").map(cell => cell.trim());
    }

    const headers = splitRow(header);

    let html = "<table><thead><tr>";

    for (const cell of headers) {
        html += "<th>" + inlineMarkdown(cell) + "</th>";
    }

    html += "</tr></thead><tbody>";

    let i = start + 2;

    while (i < lines.length) {
        const line = lines[i];

        if (!line.trim() || !line.includes("|")) {
            break;
        }

        const cells = splitRow(line);

        html += "<tr>";

        for (let j = 0; j < headers.length; j++) {
            html += "<td>" +
                inlineMarkdown(cells[j] ?? "") +
                "</td>";
        }

        html += "</tr>";

        i++;
    }

    html += "</tbody></table>";

    return {
        html,
        next: i
    };
}


function parseMarkdown(markdown) {
    // Normalisation
    markdown = markdown
        .replace(/\r\n/g, "\n")
        .replace(/\r/g, "\n");

    const lines = markdown.split("\n");

    let html = "";
    let paragraph = [];
    let i = 0;


    function flushParagraph() {
        if (paragraph.length === 0) {
            return;
        }

        const text = paragraph.join("\n");

        html += "<p>" +
            inlineMarkdown(text).replace(/\n/g, "<br>") +
            "</p>";

        paragraph = [];
    }


    while (i < lines.length) {
        const line = lines[i];


        // Ligne vide
        if (!line.trim()) {
            flushParagraph();
            i++;
            continue;
        }


        // Bloc de code ```
        if (/^\s*```/.test(line)) {
            flushParagraph();

            const language =
                line.replace(/^\s*```/, "").trim();

            const codeLines = [];

            i++;

            while (
                i < lines.length &&
                !/^\s*```/.test(lines[i])
            ) {
                codeLines.push(lines[i]);
                i++;
            }

            if (i < lines.length) {
                i++;
            }

            const className = language
                ? ` class="language-${escapeHtml(language)}"`
                : "";

            html +=
                `<pre><code${className}>` +
                escapeHtml(codeLines.join("\n")) +
                "</code></pre>";

            continue;
        }


        // Titres # a ######
        const heading = line.match(
            /^\s*(#{1,6})\s+(.+?)\s*#*\s*$/
        );

        if (heading) {
            flushParagraph();

            const level = heading[1].length;
            const content = heading[2];

            html +=
                `<h${level}>${inlineMarkdown(content)}</h${level}>`;

            i++;
            continue;
        }


        // Separateur ---
        if (/^\s*((\*\s*){3,}|(-\s*){3,}|(_\s*){3,})$/.test(line)) {
            flushParagraph();

            html += "<hr>";

            i++;
            continue;
        }


        // Citation >
        if (/^\s*>/.test(line)) {
            flushParagraph();

            const quoteLines = [];

            while (
                i < lines.length &&
                /^\s*>/.test(lines[i])
            ) {
                quoteLines.push(
                    lines[i].replace(/^\s*>\s?/, "")
                );

                i++;
            }

            html +=
                "<blockquote>" +
                parseMarkdown(quoteLines.join("\n")) +
                "</blockquote>";

            continue;
        }


        // Tableau
        if (
            i + 1 < lines.length &&
            line.includes("|") &&
            isTableSeparator(lines[i + 1])
        ) {
            flushParagraph();

            const table = parseTable(lines, i);

            if (table) {
                html += table.html;
                i = table.next;
                continue;
            }
        }


        // Liste
        /* simple */
        const listMatch = line.match(
            /^\s*([-*+]|\d+\.)\s+(.+)$/
        );

        if (listMatch) {
            flushParagraph();

            const ordered = /^\d+\./.test(listMatch[1]);
            const tag = ordered ? "ol" : "ul";

            html += `<${tag}>`;

            while (i < lines.length) {
                const item = lines[i].match(
                    /^\s*([-*+]|\d+\.)\s+(.+)$/
                );

                if (!item) {
                    break;
                }

                const currentOrdered =
                    /^\d+\./.test(item[1]);

                if (currentOrdered !== ordered) {
                    break;
                }

                html +=
                    "<li>" +
                    inlineMarkdown(item[2]) +
                    "</li>";

                i++;
            }

            html += `</${tag}>`;

            continue;
        }


        // Sinon : paragraphe
        paragraph.push(line);
        i++;
    }

    flushParagraph();

    return html;
}


// Exemple
const markdown_example = `
# Mon document

Voici un texte avec du **gras**, de l'*italique* et du ~~barre~~.

## Une liste

- Premier element
- Deuxieme element
- **Troisieme element**

## Une liste numerotee

1. Premiere etape
2. Deuxieme etape
3. Troisieme etape

## Un lien

[Mangedisque](https://mangedisque.com)

## Une citation

> Ceci est une citation.

## Un tableau

| Nom | Age | Ville |
| --- | ---: | --- |
| Alice | 25 | Paris |
| Bob | 31 | Lyon |

## Du code

\`\`\`javascript
function hello() {
    console.log("Bonjour");
}
\`\`\`

![Une jolie image sur le web](https://engrenage.studio/art/logo_almart_tech1_ret_med.png){200}
![Une jolie image sur le web](https://engrenage.studio/art/logo_almart_tech1_ret_med.png){200x100}

Et meme du script dans des balises script (mais je le met peut etre pas car ca plante mon jsminifieur donc je exceptionne dans mon minifieur):

<script>
    alert("CE CODE NE S'EXECUTERA PAS");
</script>
`;

function load_markdown( div_id, markdown_content =  markdown_example )
{
    document.getElementById( div_id ).innerHTML = parseMarkdown(markdown);
}


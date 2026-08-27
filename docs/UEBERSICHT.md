# Übersicht: KI-Agenten, Helfer & Plattformen

> Persönliche Referenz, um beim nächsten Start die Verbindungen schnell wiederzufinden.
> Stand: 2026-08-27 · Projekt: **Das Lebendige Archiv** (`jonason92/sajon-platform`)

## 1. KI-Agenten & Helfer

| Agent / Helfer | Rolle | Wo / System | Konto · Username | Starten / Verbinden | Notizen |
|---|---|---|---|---|---|
| **DeepSeek Harness** | Agenten-Orchestrierung, GUI, Cordis-Plugins | lokal · Node.js | kein einheitlicher Login (lokal); optional `dsh-auth-gate` (z. B. `admin`) | `npx @deepseek-ai/dsh web` → http://127.0.0.1:3080 | braucht `DEEPSEEK_API_KEY` |
| **DeepSeek (Modell)** | Sprach-/Arbeitsmodell („ich“) | DeepSeek-API | DeepSeek-Konto · API-Key | https://platform.deepseek.com | Modell `deepseek-*` |
| **Kimi (Moonshot)** | KI-Assistent, Video-/Audio-Transkription | lokal · GUI (Electron) | Moonshot-Konto `?` | `D:\Windows\WUModels\Kimi\Kimi.exe` | v3.2.2, ffmpeg enthalten; **kein CLI** |
| **GitHub Copilot** | Code-Assist (VS Code / github.com) | GitHub | GitHub `jonason92` | VS Code / https://github.com/copilot | gratis für Student·innen & OSS-Maintainer |
| **Voila** | dritter Helfer `?` | `?` | `?` | `?` | bitte ergänzen |

## 2. Plattformen / Systeme

| System | Zweck | Konto · Username | URL / Pfad | Notizen |
|---|---|---|---|---|
| **GitHub** | Repo, GitHub Pages, Actions, Copilot | `jonason92` (Owner) | https://github.com/jonason92/sajon-platform | weitere Handles: `JSwizzle99`, `josepp99`, `sajondocs`, `jonason`, `Sajon92`, `johnnyhaeusler98`, `invalidenC`, `Johnny Häusler`, `Sqjon GmbH` |
| **Proton** | Drive, Mail, VPN | `jonason@protonmail.ch` | https://proton.me · lokal `D:\PROTON-DRIVE LOCAL` | Mail-Adresse aus dem Buch |
| **Infomaniak** | kDrive (Cloud-Sync), Mail | Infomaniak-Konto `?` | `C:\Users\jonas\kDrive` | Projektordner liegt in kDrive |
| **MyST Markdown / Executable Books** | Buch-Tooling (Jupyter Book, MyST, Sphinx) | kein Konto | https://executablebooks.org · CLI `jupyter-book`/`myst` | `jupyter-book==1.0.4.post1` |

## 3. Schnell wiederfinden (Cheatsheet)

| Was | Wo |
|---|---|
| Harness-GUI | http://127.0.0.1:3080 |
| Live-Site | https://jonason92.github.io/sajon-platform/ |
| Projekt lokal | `C:\Users\jonas\kDrive\MAGISCHER IDEALISMUS\Magische Bücher` |
| Transkription (Intake/Output) | `D:\Projects\kimi-helfer\` (`Video-Transkription\` → `Transkripte-Aufbereitet\`) |
| Kimi-App | `D:\Windows\WUModels\Kimi\Kimi.exe` |
| Copilot | VS Code → Copilot-Chat (GitHub-Login) |
| Proton Drive | `D:\PROTON-DRIVE LOCAL` |

## 4. Offene Lücken (bitte ergänzen)

- Kimi/Moonshot-Konto (Username/E-Mail)?
- **Voila** — was ist es, welches Konto/System?
- Infomaniak-Konto (Login/Mail)?
- Wo liegt der **DeepSeek-API-Key** (Umgebungsvariable / Datei)?
- GitHub-Copilot: gratis (Student/OSS) oder bezahlt?

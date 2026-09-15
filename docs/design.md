# Design — The Lenny Growth Assistant

## 1. Design direction

The interface follows a premium product-workspace aesthetic:

- warm off-white background
- dark high-contrast typography
- restrained coral/orange accent
- rounded cards
- thin borders
- compact status indicators
- generous whitespace
- clear hierarchy

The goal is **Linear × Claude × Lenny** rather than a generic chatbot.

## 2. Information architecture

```text
Lenny Growth Assistant
│
├── Ask Lenny
│   ├── Conversation
│   ├── Composer
│   └── Evidence Trail
│
├── Knowledge Explorer
│
├── Artifact Studio
│   ├── Ship 30
│   └── Decision Canvas
│
└── System Status
    ├── API
    ├── Model
    └── Retrieval
```

The current implementation prioritizes Ask Lenny, Evidence Trail, and Artifact Studio because they directly support the assignment's core flows.

## 3. Main layout

Desktop:

```text
┌──────────────┬──────────────────────────────┬────────────────────┐
│              │                              │                    │
│   Sidebar    │          Chat                │  Evidence /        │
│              │                              │  Artifact Viewer    │
│  Workspace   │                              │                    │
│              │                              │                    │
│  Sessions    │                              │                    │
│              │                              │                    │
│              │        Composer               │                    │
└──────────────┴──────────────────────────────┴────────────────────┘
```

The right panel is deliberately persistent so evidence never disappears behind another route.

## 4. Core interaction states

### Empty state

Headline:

> What are you trying to figure out?

The empty state offers three useful starter questions rather than generic examples.

### Loading state

The assistant shows:

> Searching the knowledge base…

This tells the user that retrieval is happening instead of making the interface look frozen.

### Answer state

The assistant response is shown in the conversation.

The Evidence Trail updates with:

- source number
- title
- guest
- relevance
- source link

### Artifact state

The right panel becomes Artifact Studio.

The artifact is rendered rather than shown as raw HTML.

### Failure state

Failures should be understandable:

- backend unavailable
- Ollama unavailable
- generation timeout
- empty retrieval
- artifact failure

The user should receive a useful explanation instead of a stack trace.

## 5. Evidence Trail

The Evidence Trail is a core trust feature.

Each source card contains:

```text
01
Episode title
Guest
Relevance 0.70
↗
```

A grounding card explains:

> Answer generated from retrieved evidence rather than model-only knowledge.

The evidence panel is the server-authoritative provenance layer.

## 6. Artifact Viewer

The Artifact Viewer supports:

- rendered preview
- copy
- sanitized indicator
- artifact type
- sandboxed iframe

The generated document is displayed beside the conversation so the user does not lose context.

## 7. Interaction design

### Buttons

Buttons use verbs:

- New session
- Ship 30
- Decision Canvas
- Send

### Loading

Buttons are disabled during generation to prevent duplicate requests.

### Composer

- Enter = send
- Shift + Enter = newline
- empty message = disabled

## 8. Responsive behavior

Desktop is the primary evaluation environment.

At narrower widths:

- sidebar should reduce or collapse
- right panel can become a secondary panel
- chat should remain the primary surface
- composer remains fixed near the bottom

The core information order is:

1. conversation
2. composer
3. evidence/artifact

## 9. Accessibility

- semantic buttons
- textarea instead of contenteditable
- visible focus states
- `aria-label` for icon-only controls
- links use normal browser semantics
- iframe has a title
- disabled states are explicit
- color is not the only indicator of status

## 10. Security UX

The UI explicitly communicates:

> Generated HTML is sandboxed

and:

> Sanitized

This turns an invisible security implementation into something an evaluator can understand.

## 11. Design trade-offs

### Persistent right panel

Chosen because provenance and artifacts are part of the product, not secondary debug information.

### Compact sidebar

Chosen to preserve more horizontal space for the actual reasoning workflow.

### Warm neutral palette

Chosen to differentiate the product from the default dark AI-tool aesthetic while keeping long-form reading comfortable.

### No raw HTML injection

The UI never needs `dangerouslySetInnerHTML` for generated artifacts. It uses `srcDoc` in a sandboxed iframe.

## 12. Future design improvements

- source passage expansion
- citation hover cards
- streaming response state
- artifact tabs for Preview / Markdown / HTML
- fullscreen artifact mode
- Knowledge Explorer
- challenge-my-answer mode
- Decision Canvas editing
- mobile navigation

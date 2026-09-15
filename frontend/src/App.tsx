import {
  useCallback,
  useEffect,
  useState,
  type KeyboardEvent,
} from "react";
import {
  Activity,
  BookOpen,
  Check,
  ChevronRight,
  Copy,
  ExternalLink,
  FileText,
  LayoutDashboard,
  Loader2,
  MessageSquare,
  Plus,
  Send,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import "./App.css";

const API = "http://127.0.0.1:8000";

/* =========================================================
   TYPES
========================================================= */

type Session = {
  id: string;
  title: string;
  mode: string;
  created_at: string;
  updated_at: string;
};

type Message = {
  id: string;
  session_id: string;
  role: string;
  content: string;
  created_at: string;
};

type Source = {
  source_number: number;
  title: string;
  guest?: string;
  episode?: string;
  source_url?: string;
  relevance: number;
};

type Artifact = {
  id: string;
  session_id: string;
  title: string;
  artifact_type: string;
  content_format: string;
  content: string;
  sanitized_content?: string;
  created_at?: string;
  updated_at?: string;
};

type SystemStatus = {
  status: string;
  provider?: string;
  model?: string;
  database?: string;
  retrieval?: string;
  artifact_sanitization?: boolean;
};

type ApiError = {
  message?: string;
  detail?: string;
};

type SendMessageResponse = {
  message: Message;
  provider: string;
  model: string;
  sources: Source[];
};

/* =========================================================
   HELPERS
========================================================= */

function getErrorMessage(data: ApiError): string {
  return data.message || data.detail || "Request failed";
}

/* =========================================================
   APP
========================================================= */

function App() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [session, setSession] = useState<Session | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [artifact, setArtifact] = useState<Artifact | null>(null);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [artifactLoading, setArtifactLoading] =
    useState(false);
  const [copied, setCopied] = useState(false);

  const [systemStatus, setSystemStatus] =
    useState<SystemStatus | null>(null);

  /* =======================================================
     OPEN SESSION
  ======================================================= */

  const openSession = useCallback(
    async (item: Session) => {
      setSession(item);
      setArtifact(null);
      setSources([]);

      try {
        const response = await fetch(
          `${API}/api/sessions/${item.id}/messages`
        );

        const data:
          | Message[]
          | ApiError = await response.json();

        if (!response.ok) {
          throw new Error(
            getErrorMessage(data as ApiError)
          );
        }

        setMessages(data as Message[]);
      } catch (error: unknown) {
        console.error(
          "Failed to load session:",
          error
        );

        setMessages([]);
      }
    },
    []
  );

  /* =======================================================
     CREATE SESSION
  ======================================================= */

  const createSession = useCallback(async () => {
    try {
      const response = await fetch(
        `${API}/api/sessions`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            title: "New Lenny Session",
            mode: "ask",
          }),
        }
      );

      const data:
        | Session
        | ApiError = await response.json();

      if (!response.ok) {
        throw new Error(
          getErrorMessage(data as ApiError)
        );
      }

      const newSession = data as Session;

      setSessions((previous) => [
        newSession,
        ...previous,
      ]);

      setSession(newSession);
      setMessages([]);
      setSources([]);
      setArtifact(null);
    } catch (error: unknown) {
      console.error(
        "Failed to create session:",
        error
      );
    }
  }, []);

  /* =======================================================
     LOAD SYSTEM STATUS
  ======================================================= */

  const loadStatus = useCallback(async () => {
    try {
      const response = await fetch(
        `${API}/api/system/status`
      );

      const data:
        | SystemStatus
        | ApiError = await response.json();

      if (!response.ok) {
        throw new Error(
          getErrorMessage(data as ApiError)
        );
      }

      setSystemStatus(data as SystemStatus);
    } catch (error: unknown) {
      console.error(
        "Failed to load system status:",
        error
      );

      setSystemStatus({
        status: "offline",
      });
    }
  }, []);

  /* =======================================================
     LOAD SESSIONS
  ======================================================= */

  const loadSessions = useCallback(async () => {
    try {
      const response = await fetch(
        `${API}/api/sessions`
      );

      const data:
        | Session[]
        | ApiError = await response.json();

      if (!response.ok) {
        throw new Error(
          getErrorMessage(data as ApiError)
        );
      }

      const sessionList = data as Session[];

      setSessions(sessionList);

      if (sessionList.length > 0) {
        await openSession(sessionList[0]);
      } else {
        await createSession();
      }
    } catch (error: unknown) {
      console.error(
        "Failed to load sessions:",
        error
      );
    }
  }, [openSession, createSession]);

  /* =======================================================
     INITIALIZE APP
     
     React's new set-state-in-effect rule flags the
     initialization calls because the called functions
     eventually update state from API responses.

     This is intentionally disabled only for this effect.
  ======================================================= */

  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    void loadSessions();
    void loadStatus();
  }, [loadSessions, loadStatus]);
  /* eslint-enable react-hooks/set-state-in-effect */

  /* =======================================================
     SEND MESSAGE
  ======================================================= */

  async function sendMessage() {
    if (!input.trim() || !session || loading) {
      return;
    }

    const content = input.trim();

    setInput("");
    setLoading(true);

    const optimisticMessage: Message = {
      id: crypto.randomUUID(),
      session_id: session.id,
      role: "user",
      content,
      created_at: new Date().toISOString(),
    };

    setMessages((previous) => [
      ...previous,
      optimisticMessage,
    ]);

    try {
      const response = await fetch(
        `${API}/api/sessions/${session.id}/messages`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            content,
          }),
        }
      );

      const data:
        | SendMessageResponse
        | ApiError = await response.json();

      if (!response.ok) {
        throw new Error(
          getErrorMessage(data as ApiError)
        );
      }

      const result =
        data as SendMessageResponse;

      setMessages((previous) => [
        ...previous,
        {
          ...result.message,
          role: "assistant",
        },
      ]);

      setSources(result.sources || []);
    } catch (error: unknown) {
      console.error(
        "Message request failed:",
        error
      );

      const errorMessage =
        error instanceof Error
          ? error.message
          : "Unable to complete the request.";

      setMessages((previous) => [
        ...previous,
        {
          id: crypto.randomUUID(),
          session_id: session.id,
          role: "assistant",
          content:
            "I couldn't complete that request.\n\n" +
            `${errorMessage}\n\n` +
            "Please check that the backend and Ollama are running.",
          created_at:
            new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  /* =======================================================
     CREATE DECISION CANVAS
  ======================================================= */

  async function createArtifact() {
    if (!session || artifactLoading) {
      return;
    }

    setArtifactLoading(true);

    try {
      const response = await fetch(
        `${API}/api/sessions/${session.id}/artifacts`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            prompt:
              "Create a product-market fit decision canvas " +
              "for an early-stage startup. Include the " +
              "problem, evidence, options, trade-offs, " +
              "recommendation, and next experiment.",
            artifact_type: "decision_canvas",
          }),
        }
      );

      const data:
        | Artifact
        | ApiError = await response.json();

      if (!response.ok) {
        throw new Error(
          getErrorMessage(data as ApiError)
        );
      }

      setArtifact(data as Artifact);
    } catch (error: unknown) {
      console.error(
        "Artifact generation failed:",
        error
      );

      const message =
        error instanceof Error
          ? error.message
          : "Artifact generation failed.";

      alert(message);
    } finally {
      setArtifactLoading(false);
    }
  }

  /* =======================================================
     CREATE SHIP 30
  ======================================================= */

  async function createShip30() {
    if (!session || artifactLoading) {
      return;
    }

    setArtifactLoading(true);

    try {
      const response = await fetch(
        `${API}/api/sessions/${session.id}/artifacts`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            prompt:
              "Write a Ship 30 for 30 style essay about " +
              "how an early-stage startup should find " +
              "product-market fit. Make it practical, " +
              "specific, evidence-grounded, skimmable, " +
              "with a strong hook and clear takeaway.",
            artifact_type: "ship30",
          }),
        }
      );

      const data:
        | Artifact
        | ApiError = await response.json();

      if (!response.ok) {
        throw new Error(
          getErrorMessage(data as ApiError)
        );
      }

      setArtifact(data as Artifact);
    } catch (error: unknown) {
      console.error(
        "Ship30 generation failed:",
        error
      );

      const message =
        error instanceof Error
          ? error.message
          : "Ship30 generation failed.";

      alert(message);
    } finally {
      setArtifactLoading(false);
    }
  }

  /* =======================================================
     COPY ARTIFACT
  ======================================================= */

  async function copyArtifact() {
    if (!artifact) {
      return;
    }

    try {
      await navigator.clipboard.writeText(
        artifact.sanitized_content ||
          artifact.content
      );

      setCopied(true);

      window.setTimeout(() => {
        setCopied(false);
      }, 1500);
    } catch (error: unknown) {
      console.error(
        "Failed to copy artifact:",
        error
      );
    }
  }

  /* =======================================================
     KEYBOARD
  ======================================================= */

  function handleKeyDown(
    event: KeyboardEvent<HTMLTextAreaElement>
  ) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      void sendMessage();
    }
  }

  /* =======================================================
     UI
  ======================================================= */

  return (
    <div className="app-shell">

      {/* =================================================
          SIDEBAR
      ================================================= */}

      <aside className="sidebar">

        <div className="brand">
          <div className="brand-icon">
            <Sparkles size={18} />
          </div>

          <div>
            <div className="brand-name">
              Lenny
            </div>

            <div className="brand-sub">
              Growth Assistant
            </div>
          </div>
        </div>

        <button
          className="new-session"
          onClick={() =>
            void createSession()
          }
        >
          <Plus size={17} />
          New session
        </button>

        <div className="sidebar-label">
          WORKSPACE
        </div>

        <button className="nav-item active">
          <MessageSquare size={17} />
          Ask Lenny
        </button>

        <button className="nav-item">
          <BookOpen size={17} />
          Knowledge Explorer
        </button>

        <button className="nav-item">
          <LayoutDashboard size={17} />
          Artifact Studio
        </button>

        <div className="sidebar-label session-label">
          RECENT SESSIONS
        </div>

        <div className="session-list">
          {sessions.map((item) => (
            <button
              key={item.id}
              className={`session-item ${
                session?.id === item.id
                  ? "selected"
                  : ""
              }`}
              onClick={() =>
                void openSession(item)
              }
            >
              <MessageSquare size={14} />

              <span>
                {item.title}
              </span>
            </button>
          ))}
        </div>

        <div className="sidebar-bottom">

          <div className="health-card">

            <div className="health-top">
              <Activity size={15} />

              <span>
                System status
              </span>

              <span
                className={`status-dot ${
                  systemStatus?.status === "ok"
                    ? "online"
                    : ""
                }`}
              />
            </div>

            <div className="health-row">
              <span>
                API
              </span>

              <b>
                {systemStatus?.status ===
                "ok"
                  ? "Healthy"
                  : "Checking"}
              </b>
            </div>

            <div className="health-row">
              <span>
                Model
              </span>

              <b>
                {systemStatus?.model ||
                  "—"}
              </b>
            </div>

            <div className="health-row">
              <span>
                Retrieval
              </span>

              <b>
                {systemStatus?.retrieval ||
                  "—"}
              </b>
            </div>

          </div>

          <div className="security-note">
            <ShieldCheck size={15} />

            Generated HTML is sandboxed
          </div>

        </div>
      </aside>

      {/* =================================================
          MAIN
      ================================================= */}

      <main className="main">

        {/* TOP BAR */}

        <header className="topbar">

          <div>
            <div className="eyebrow">
              GROWTH COPILOT
            </div>

            <h1>
              Ask Lenny
            </h1>
          </div>

          <div className="provider-pill">

            <span className="provider-dot" />

            {systemStatus?.provider ||
              "ollama"}

            <span className="divider" />

            {systemStatus?.model ||
              "qwen3:4b"}

          </div>

        </header>

        <div className="workspace">

          {/* =================================================
              CHAT
          ================================================= */}

          <section className="chat-panel">

            <div className="chat-scroll">

              {messages.length === 0 ? (

                <div className="welcome">

                  <div className="welcome-icon">
                    <Sparkles size={27} />
                  </div>

                  <h2>
                    What are you trying to
                    figure out?
                  </h2>

                  <p>
                    Ask questions grounded in
                    Lenny&apos;s Podcast
                    knowledge. Get evidence,
                    context, and actionable
                    next steps.
                  </p>

                  <div className="suggestions">

                    <button
                      onClick={() =>
                        setInput(
                          "How should an early-stage startup find product-market fit?"
                        )
                      }
                    >
                      <span>
                        01
                      </span>

                      How should an
                      early-stage startup
                      find PMF?

                      <ChevronRight size={15} />
                    </button>

                    <button
                      onClick={() =>
                        setInput(
                          "What are the strongest signals that a product has product-market fit?"
                        )
                      }
                    >
                      <span>
                        02
                      </span>

                      What are the
                      strongest PMF
                      signals?

                      <ChevronRight size={15} />
                    </button>

                    <button
                      onClick={() =>
                        setInput(
                          "How should a startup prioritize its next growth experiment?"
                        )
                      }
                    >
                      <span>
                        03
                      </span>

                      How should I
                      prioritize growth
                      experiments?

                      <ChevronRight size={15} />
                    </button>

                  </div>

                </div>

              ) : (

                <div className="messages">

                  {messages.map(
                    (message) => (

                      <div
                        key={message.id}
                        className={`message ${
                          message.role ===
                          "user"
                            ? "user"
                            : "assistant"
                        }`}
                      >

                        <div className="message-avatar">
                          {message.role ===
                          "user"
                            ? "K"
                            : "L"}
                        </div>

                        <div className="message-body">

                          <div className="message-role">
                            {message.role ===
                            "user"
                              ? "You"
                              : "Lenny"}
                          </div>

                          <div className="message-content">
                            {message.content}
                          </div>

                        </div>

                      </div>

                    )
                  )}

                  {loading && (

                    <div className="message assistant">

                      <div className="message-avatar">
                        L
                      </div>

                      <div className="message-body">

                        <div className="message-role">
                          Lenny
                        </div>

                        <div className="thinking">

                          <Loader2
                            size={16}
                            className="spin"
                          />

                          Searching the
                          knowledge base…

                        </div>

                      </div>

                    </div>

                  )}

                </div>

              )}

            </div>

            {/* COMPOSER */}

            <div className="composer-area">

              <div className="quick-actions">

                <button
                  onClick={() =>
                    void createShip30()
                  }
                  disabled={
                    artifactLoading
                  }
                >
                  <FileText size={14} />

                  {artifactLoading
                    ? "Generating..."
                    : "Ship 30"}
                </button>

                <button
                  onClick={() =>
                    void createArtifact()
                  }
                  disabled={
                    artifactLoading
                  }
                >
                  <LayoutDashboard
                    size={14}
                  />

                  {artifactLoading
                    ? "Generating..."
                    : "Decision Canvas"}
                </button>

              </div>

              <div className="composer">

                <textarea
                  value={input}
                  onChange={(event) =>
                    setInput(
                      event.target.value
                    )
                  }
                  onKeyDown={handleKeyDown}
                  placeholder="Ask a product or growth question..."
                  rows={2}
                  disabled={loading}
                />

                <button
                  className="send-button"
                  onClick={() =>
                    void sendMessage()
                  }
                  disabled={
                    !input.trim() ||
                    loading
                  }
                  aria-label="Send message"
                >

                  {loading ? (
                    <Loader2
                      size={18}
                      className="spin"
                    />
                  ) : (
                    <Send size={18} />
                  )}

                </button>

              </div>

              <div className="composer-footer">

                <span>
                  Enter to send · Shift +
                  Enter for new line
                </span>

                <span>
                  Grounded in
                  Lenny&apos;s knowledge
                  base
                </span>

              </div>

            </div>

          </section>

          {/* =================================================
              RIGHT PANEL
          ================================================= */}

          <aside className="right-panel">

            <div className="panel-header">

              <div>

                <div className="panel-kicker">
                  {artifact
                    ? "ARTIFACT STUDIO"
                    : "EVIDENCE TRAIL"}
                </div>

                <h3>
                  {artifact
                    ? artifact.title
                    : "Knowledge sources"}
                </h3>

              </div>

              {artifact && (

                <button
                  className="icon-button"
                  onClick={() =>
                    void copyArtifact()
                  }
                  aria-label="Copy artifact"
                >

                  {copied ? (
                    <Check size={16} />
                  ) : (
                    <Copy size={16} />
                  )}

                </button>

              )}

            </div>

            {/* ARTIFACT */}

            {artifact ? (

              <div className="artifact-viewer">

                <div className="artifact-meta">

                  <span className="artifact-type">
                    {artifact.artifact_type}
                  </span>

                  <span>
                    <ShieldCheck
                      size={13}
                    />

                    Sanitized
                  </span>

                </div>

                <div className="preview-frame">

                  <iframe
                    title="Generated artifact"
                    sandbox=""
                    srcDoc={
                      artifact.sanitized_content ||
                      artifact.content
                    }
                  />

                </div>

              </div>

            ) : sources.length > 0 ? (

              /* EVIDENCE */

              <div className="sources">

                <div className="grounding-card">

                  <div className="grounding-indicator">

                    <span />

                    High grounding

                  </div>

                  <p>
                    Answer generated from
                    retrieved evidence rather
                    than model-only knowledge.
                  </p>

                </div>

                {sources.map((source) => (

                  <div
                    className="source-card"
                    key={
                      source.source_number
                    }
                  >

                    <div className="source-number">
                      {String(
                        source.source_number
                      ).padStart(2, "0")}
                    </div>

                    <div className="source-info">

                      <div className="source-title">
                        {source.title}
                      </div>

                      {source.guest && (

                        <div className="source-guest">
                          {source.guest}
                        </div>

                      )}

                      <div className="source-bottom">

                        <span>
                          Relevance{" "}
                          {source.relevance?.toFixed(
                            2
                          )}
                        </span>

                        {source.source_url && (

                          <a
                            href={
                              source.source_url
                            }
                            target="_blank"
                            rel="noreferrer"
                            aria-label="Open source"
                          >
                            <ExternalLink
                              size={12}
                            />
                          </a>

                        )}

                      </div>

                    </div>

                  </div>

                ))}

              </div>

            ) : (

              /* EMPTY STATE */

              <div className="empty-evidence">

                <div className="empty-icon">
                  <BookOpen size={20} />
                </div>

                <h4>
                  Evidence appears here
                </h4>

                <p>
                  Ask Lenny a question and
                  the retrieved podcast
                  evidence will appear here
                  with source tracing.
                </p>

              </div>

            )}

            {artifact && (

              <div className="artifact-footer">

                <ShieldCheck size={15} />

                Preview runs inside a
                sandboxed iframe with
                sanitized HTML.

              </div>

            )}

          </aside>

        </div>

      </main>

    </div>
  );
}

export default App;
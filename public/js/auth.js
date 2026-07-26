/**
 * Zafra AI — Autenticación con Supabase Auth
 */
(function () {
  let client = null;

  function assertConfig() {
    const cfg = window.SUPABASE_CONFIG;
    if (!cfg?.url || !cfg?.anonKey) {
      throw new Error("Falta configurar frontend/js/supabase-config.js");
    }
    if (
      cfg.anonKey === "tu-clave-anon-aqui"
      || cfg.anonKey === "tu-clave-anon"
    ) {
      throw new Error(
        "Pegá tu anon key de Supabase en frontend/js/supabase-config.js "
        + "(Project Settings → API)."
      );
    }
    if (!window.supabase?.createClient) {
      throw new Error("No se cargó la librería de Supabase.");
    }
  }

  function getClient() {
    if (!client) {
      assertConfig();
      client = window.supabase.createClient(
        window.SUPABASE_CONFIG.url,
        window.SUPABASE_CONFIG.anonKey,
      );
    }
    return client;
  }

  async function getSession() {
    const { data, error } = await getClient().auth.getSession();
    if (error) throw error;
    return data.session;
  }

  async function getAccessToken() {
    const session = await getSession();
    return session?.access_token ?? null;
  }

  async function requireAuth() {
    const session = await getSession();
    if (!session) {
      window.location.replace("/");
      return null;
    }
    return session;
  }

  async function signOut() {
    await getClient().auth.signOut();
    window.location.replace("/");
  }

  function bindHeader(session) {
    const emailEl = document.getElementById("auth-user-email");
    const btnLogout = document.getElementById("btn-logout");
    if (emailEl) emailEl.textContent = session.user.email || "Usuario";
    if (btnLogout) {
      btnLogout.addEventListener("click", async () => {
        btnLogout.disabled = true;
        await signOut();
      });
    }
  }

  async function initProtectedPage() {
    const session = await requireAuth();
    if (session) bindHeader(session);
    return session;
  }

  function clearAuthMessages() {
    ["login-error", "login-success"].forEach((id) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.textContent = "";
      el.hidden = true;
    });
  }

  function showLoginError(message) {
    const el = document.getElementById("login-error");
    const successEl = document.getElementById("login-success");
    if (successEl) successEl.hidden = true;
    if (!el) return;
    el.textContent = message;
    el.hidden = !message;
  }

  function showLoginSuccess(message) {
    const el = document.getElementById("login-success");
    const errorEl = document.getElementById("login-error");
    if (errorEl) errorEl.hidden = true;
    if (!el) return;
    el.textContent = message;
    el.hidden = !message;
  }

  function setRegisterMode(register, refs) {
    const { form, toggleBtn, modeHint } = refs;
    refs.isRegister = register;

    if (modeHint) {
      modeHint.textContent = register
        ? "Creá una cuenta con email y contraseña."
        : "Ingresá con tu email y contraseña.";
    }
    if (toggleBtn) {
      toggleBtn.textContent = register
        ? "¿Ya tenés cuenta? Iniciar sesión"
        : "¿No tenés cuenta? Registrarse";
    }
    const submitText = document.querySelector("#btn-login .btn__text");
    if (submitText) {
      submitText.textContent = register ? "Crear cuenta" : "Iniciar sesión";
    }
    if (form?.password) {
      form.password.autocomplete = register ? "new-password" : "current-password";
    }
  }

  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  function normalizeAuthError(error) {
    const msg = (error?.message || "").toLowerCase();
    if (msg.includes("rate limit")) {
      return "Supabase limitó los emails por muchos intentos. Esperá 15–60 min, "
        + "desactivá «Confirm email» en Supabase, o creá el usuario con «Add user».";
    }
    if (msg.includes("already registered") || msg.includes("user already registered")) {
      return "Ese email ya está registrado. Usá «Iniciar sesión».";
    }
    if (msg.includes("email not confirmed")) {
      return "Confirmá tu cuenta desde el email de Supabase antes de iniciar sesión.";
    }
    if (msg.includes("invalid login credentials")) {
      return "Email o contraseña incorrectos. Si te registraste recién, confirmá el email primero.";
    }
    return error.message || "No se pudo completar la operación.";
  }

  function setLoginLoading(loading) {
    const btn = document.getElementById("btn-login");
    const text = btn?.querySelector(".btn__text");
    const loader = btn?.querySelector(".btn__loader");
    if (btn) btn.disabled = loading;
    if (text) text.hidden = loading;
    if (loader) loader.hidden = !loading;
  }

  async function initLoginPage() {
    const session = await getSession();
    if (session) {
      window.location.replace("app.html");
      return;
    }

    const form = document.getElementById("login-form");
    const toggleBtn = document.getElementById("btn-toggle-mode");
    const modeHint = document.getElementById("login-mode-hint");
    const refs = { form, toggleBtn, modeHint, isRegister: false };

    if (toggleBtn && modeHint) {
      toggleBtn.addEventListener("click", () => {
        setRegisterMode(!refs.isRegister, refs);
        clearAuthMessages();
      });
    }

    form?.addEventListener("submit", async (event) => {
      event.preventDefault();
      clearAuthMessages();
      setLoginLoading(true);

      const email = form.email.value.trim().toLowerCase();
      const password = form.password.value;

      if (!isValidEmail(email)) {
        showLoginError("Ingresá un email válido (ejemplo: nombre@gmail.com).");
        setLoginLoading(false);
        return;
      }

      try {
        if (refs.isRegister) {
          const { data, error } = await getClient().auth.signUp({ email, password });
          if (error) throw error;

          setRegisterMode(false, refs);
          form.password.value = "";

          showLoginSuccess(
            "¡Cuenta creada correctamente! Ahora iniciá sesión con tu email y contraseña."
          );

          if (data.session) {
            setTimeout(() => {
              window.location.replace("app.html");
            }, 2500);
          }
        } else {
          const { error } = await getClient().auth.signInWithPassword({ email, password });
          if (error) throw error;
          window.location.replace("app.html");
        }
      } catch (error) {
        showLoginError(normalizeAuthError(error));
      } finally {
        setLoginLoading(false);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    const page = document.body.dataset.page;
    if (page === "app") {
      initProtectedPage().catch((error) => {
        console.error(error);
        alert(error.message);
      });
    }
    if (page === "login") {
      initLoginPage().catch((error) => {
        console.error(error);
        showLoginError(error.message);
      });
    }
  });

  window.ZafraAuth = {
    getSession,
    getAccessToken,
    requireAuth,
    signOut,
    initProtectedPage,
    initLoginPage,
  };
})();

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

  function showLoginError(message) {
    const el = document.getElementById("login-error");
    if (!el) return;
    el.textContent = message;
    el.hidden = !message;
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
    let isRegister = false;

    if (toggleBtn && modeHint) {
      toggleBtn.addEventListener("click", () => {
        isRegister = !isRegister;
        modeHint.textContent = isRegister
          ? "Creá una cuenta con email y contraseña."
          : "Ingresá con tu email y contraseña.";
        toggleBtn.textContent = isRegister
          ? "¿Ya tenés cuenta? Iniciar sesión"
          : "¿No tenés cuenta? Registrarse";
        const submitText = document.querySelector("#btn-login .btn__text");
        if (submitText) {
          submitText.textContent = isRegister ? "Crear cuenta" : "Iniciar sesión";
        }
        showLoginError("");
      });
    }

    form?.addEventListener("submit", async (event) => {
      event.preventDefault();
      showLoginError("");
      setLoginLoading(true);

      const email = form.email.value.trim();
      const password = form.password.value;

      try {
        if (isRegister) {
          const { error } = await getClient().auth.signUp({ email, password });
          if (error) throw error;
          showLoginError(
            "Cuenta creada. Revisá tu email para confirmar (si Confirm email está activo) "
            + "y luego iniciá sesión."
          );
          isRegister = false;
          toggleBtn?.click();
        } else {
          const { error } = await getClient().auth.signInWithPassword({ email, password });
          if (error) throw error;
          window.location.replace("app.html");
        }
      } catch (error) {
        showLoginError(error.message || "No se pudo completar la operación.");
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

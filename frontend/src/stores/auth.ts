import { call } from "frappe-ui";
import { defineStore } from "pinia";
import { computed, ref } from "vue";

function getSessionUser(): string | null {
  const cookies = new URLSearchParams(document.cookie.split("; ").join("&"));
  const userId = cookies.get("user_id");
  return userId && userId !== "Guest" ? userId : null;
}

export const useAuthStore = defineStore("auth", () => {
  const user = ref(getSessionUser());
  const fullName = ref((window as any).full_name || "");
  const isLoggedIn = computed(() => !!user.value);

  async function logout() {
    await call("logout");
    window.location.href = "/login?redirect-to=/portal";
  }

  return { isLoggedIn, user, fullName, logout };
});

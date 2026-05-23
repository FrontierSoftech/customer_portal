<template>
  <div class="flex h-full w-full overflow-hidden">
    <!-- Mobile top bar -->
    <div class="fixed top-0 left-0 right-0 z-30 flex items-center gap-3 px-4 h-13 bg-surface-white border-b border-outline-gray-modals sm:hidden flex-shrink-0">
      <button
        class="text-ink-gray-6 hover:text-ink-gray-9 p-1 -ml-1"
        @click="mobileOpen = true"
      >
        <FeatherIcon name="menu" class="w-5 h-5" />
      </button>
      <span class="font-semibold text-ink-gray-9 text-sm truncate">{{ portalStore.portalTitle }}</span>
    </div>

    <!-- Mobile backdrop -->
    <transition name="fade">
      <div
        v-if="mobileOpen"
        class="fixed inset-0 z-40 bg-black/40 sm:hidden"
        @click="mobileOpen = false"
      />
    </transition>

    <Sidebar :mobile-open="mobileOpen" @close="mobileOpen = false" />

    <!-- Main: add top padding on mobile for the fixed header bar -->
    <main class="flex-1 overflow-auto pt-13 sm:pt-0">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { FeatherIcon } from "frappe-ui";
import { onMounted, ref } from "vue";
import { RouterView } from "vue-router";
import Sidebar from "../components/Sidebar.vue";
import { usePortalStore } from "../stores/portal";

const portalStore = usePortalStore();
const mobileOpen = ref(false);

onMounted(() => portalStore.load());
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

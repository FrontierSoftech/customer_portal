<template>
  <div class="flex items-center justify-center h-full text-ink-gray-5">
    <div class="text-center">
      <p class="text-lg font-medium text-ink-gray-7">Welcome to {{ portalStore.portalTitle }}</p>
      <p class="mt-1 text-sm">Select a section from the sidebar to get started.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { usePortalStore } from "../stores/portal";
const portalStore = usePortalStore();
</script>

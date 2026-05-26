<template>
  <RouterLink
    v-if="to"
    :to="to"
    class="flex items-center gap-2 px-3 py-1.5 rounded mx-1 text-sm transition-colors"
    :class="isActive
      ? 'bg-surface-gray-3 text-ink-gray-9 font-medium'
      : 'text-ink-gray-6 hover:bg-surface-gray-2 hover:text-ink-gray-9'"
  >
    <FeatherIcon :name="iconName || 'file-text'" class="w-4 h-4 flex-shrink-0" />
    <span v-if="isExpanded" class="truncate">{{ label }}</span>
  </RouterLink>
  <button
    v-else
    class="flex items-center gap-2 px-3 py-1.5 rounded mx-1 text-sm transition-colors w-full text-left"
    :class="isActive
      ? 'bg-surface-gray-3 text-ink-gray-9 font-medium'
      : 'text-ink-gray-6 hover:bg-surface-gray-2 hover:text-ink-gray-9'"
    @click="onClick && onClick()"
  >
    <FeatherIcon :name="iconName || 'file-text'" class="w-4 h-4 flex-shrink-0" />
    <span v-if="isExpanded" class="truncate">{{ label }}</span>
  </button>
</template>

<script setup lang="ts">
import { FeatherIcon } from "frappe-ui";
import { RouterLink } from "vue-router";

defineProps<{
  label: string;
  iconName?: string;
  to?: any;
  isExpanded?: boolean;
  isActive?: boolean;
  onClick?: () => void;
}>();
</script>

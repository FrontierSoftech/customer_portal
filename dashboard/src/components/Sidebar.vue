<template>
  <aside
    class="flex flex-col border-r border-outline-gray-modals bg-surface-menu-bar select-none
           fixed inset-y-0 left-0 z-50 transition-transform duration-300
           sm:static sm:translate-x-0 sm:transition-none sm:z-auto"
    :class="mobileOpen ? 'translate-x-0 shadow-xl' : '-translate-x-full'"
    :style="{ width: isExpanded ? '220px' : '52px' }"
  >
    <!-- Logo / Title / User -->
    <div class="flex items-center gap-2 px-3 py-3 border-b border-outline-gray-modals flex-shrink-0">
      <div class="flex-shrink-0 w-7 h-7 rounded bg-blue-600 flex items-center justify-center">
        <span class="text-white text-xs font-bold">
          {{ portalStore.portalTitle ? portalStore.portalTitle.slice(0, 2).toUpperCase() : 'CP' }}
        </span>
      </div>
      <div v-if="isExpanded" class="flex flex-col min-w-0">
        <span class="font-semibold text-ink-gray-9 truncate text-sm leading-tight">
          {{ portalStore.portalTitle }}
        </span>
        <span class="text-xs text-ink-gray-5 truncate leading-tight">
          {{ authStore.fullName || authStore.user }}
        </span>
      </div>
    </div>

    <!-- Nav links -->
    <nav class="flex-1 overflow-y-auto py-2">
      <SidebarLink
        v-for="dt in portalStore.doctypes"
        :key="dt.doctype_name"
        :label="dt.label"
        :icon-name="dt.icon"
        :to="{ name: 'RecordList', params: { doctypeName: dt.doctype_name } }"
        :is-expanded="isExpanded"
        :is-active="route.params.doctypeName === dt.doctype_name"
        @click="emit('close')"
      />

      <!-- ── Tasks panel: shown when viewing a Project detail ── -->
      <div
        v-if="isOnProjectDetail && isExpanded && (portalStore.loadingTasks || portalStore.projectTasks.length)"
        class="mt-2 border-t border-outline-gray-modals pt-2"
      >
        <div class="px-3 py-1 text-xs font-semibold text-ink-gray-4 uppercase tracking-wider">
          Tasks
        </div>

        <div v-if="portalStore.loadingTasks" class="px-3 py-1.5 flex items-center gap-2 text-xs text-ink-gray-4">
          <div class="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-400"></div>
          Loading…
        </div>

        <template v-else>
          <div v-if="!portalStore.projectTasks.length" class="px-3 py-1.5 text-xs text-ink-gray-4">
            No tasks
          </div>
          <div v-for="task in portalStore.projectTasks" :key="task.name">
            <!-- Task row -->
            <button
              class="flex items-center gap-2 px-3 py-1.5 rounded mx-1 text-sm w-full text-left transition-colors text-ink-gray-6 hover:bg-surface-gray-2 hover:text-ink-gray-9"
              @click="toggleTask(task.name)"
            >
              <FeatherIcon name="check-square" class="w-4 h-4 flex-shrink-0 text-ink-gray-4" />
              <span class="truncate flex-1 text-xs">{{ task.subject }}</span>
              <span class="text-xs px-1 py-0.5 rounded bg-surface-gray-2 text-ink-gray-5 flex-shrink-0">
                {{ task.status }}
              </span>
              <FeatherIcon
                v-if="task.milestones && task.milestones.length"
                :name="isTaskExpanded(task.name) ? 'chevron-down' : 'chevron-right'"
                class="w-3 h-3 flex-shrink-0 text-ink-gray-4"
              />
            </button>

            <!-- Milestone sub-items under each task -->
            <div
              v-if="task.milestones && task.milestones.length && isTaskExpanded(task.name)"
              class="ml-3 border-l border-outline-gray-modals"
            >
              <div
                v-for="ms in task.milestones"
                :key="ms.name"
                class="flex items-center gap-2 px-3 py-1 mx-1 rounded text-xs text-ink-gray-5 hover:bg-surface-gray-2 transition-colors"
              >
                <FeatherIcon name="flag" class="w-3 h-3 flex-shrink-0 text-amber-500" />
                <span class="truncate flex-1">{{ ms.subject }}</span>
                <span class="px-1 py-0.5 rounded bg-surface-gray-2 text-ink-gray-4 flex-shrink-0">
                  {{ ms.status }}
                </span>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- ── Milestones panel: shown when viewing a Task detail ── -->
      <div
        v-if="isOnTaskDetail && isExpanded && (portalStore.loadingMilestones || portalStore.taskMilestones.length)"
        class="mt-2 border-t border-outline-gray-modals pt-2"
      >
        <div class="px-3 py-1 text-xs font-semibold text-ink-gray-4 uppercase tracking-wider">
          Milestones
        </div>

        <div v-if="portalStore.loadingMilestones" class="px-3 py-1.5 flex items-center gap-2 text-xs text-ink-gray-4">
          <div class="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-400"></div>
          Loading…
        </div>

        <template v-else>
          <div v-if="!portalStore.taskMilestones.length" class="px-3 py-1.5 text-xs text-ink-gray-4">
            No milestones
          </div>
          <div
            v-for="ms in portalStore.taskMilestones"
            :key="ms.name"
            class="flex items-center gap-2 px-3 py-1.5 rounded mx-1 text-xs text-ink-gray-5 hover:bg-surface-gray-2 transition-colors"
          >
            <FeatherIcon name="flag" class="w-3 h-3 flex-shrink-0 text-amber-500" />
            <span class="truncate flex-1">{{ ms.subject }}</span>
            <span class="px-1 py-0.5 rounded bg-surface-gray-2 text-ink-gray-4 flex-shrink-0">
              {{ ms.status }}
            </span>
          </div>
        </template>
      </div>
    </nav>

    <!-- Bottom: collapse + logout -->
    <div class="flex flex-col gap-1 pb-3 border-t border-outline-gray-modals pt-2 flex-shrink-0">
      <button
        class="hidden sm:flex items-center gap-2 px-3 py-1.5 text-ink-gray-5 hover:text-ink-gray-9 hover:bg-surface-gray-2 rounded mx-1 text-sm"
        @click="isExpanded = !isExpanded"
      >
        <FeatherIcon
          :name="isExpanded ? 'chevrons-left' : 'chevrons-right'"
          class="w-4 h-4 flex-shrink-0"
        />
        <span v-if="isExpanded">Collapse</span>
      </button>
      <button
        class="flex items-center gap-2 px-3 py-1.5 text-red-500 hover:bg-red-50 rounded mx-1 text-sm"
        @click="authStore.logout()"
      >
        <FeatherIcon name="log-out" class="w-4 h-4 flex-shrink-0" />
        <span v-if="isExpanded">Log out</span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { FeatherIcon } from "frappe-ui";
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { usePortalStore } from "../stores/portal";
import SidebarLink from "./SidebarLink.vue";

defineProps<{ mobileOpen: boolean }>();
const emit = defineEmits<{ (e: "close"): void }>();

const isExpanded = ref(true);
const portalStore = usePortalStore();
const authStore = useAuthStore();
const route = useRoute();

const expandedTaskNames = ref<string[]>([]);

const isOnProjectDetail = computed(
  () => route.name === "RecordDetail" && route.params.doctypeName === "Project"
);

const isOnTaskDetail = computed(
  () => route.name === "RecordDetail" && route.params.doctypeName === "Task"
);

function toggleTask(taskName: string) {
  const idx = expandedTaskNames.value.indexOf(taskName);
  if (idx >= 0) {
    expandedTaskNames.value.splice(idx, 1);
  } else {
    expandedTaskNames.value.push(taskName);
  }
}

function isTaskExpanded(taskName: string): boolean {
  return expandedTaskNames.value.includes(taskName);
}

// React to route changes:
// - Project detail  → load tasks (+ their milestones) via get_project_tasks
// - Task detail     → load milestones for that task via get_task_milestones
// - Anything else   → clear both panels
watch(
  () => [route.name, route.params.doctypeName, route.params.name] as const,
  ([routeName, doctype, recordName]) => {
    if (routeName === "RecordDetail" && doctype === "Project" && recordName) {
      expandedTaskNames.value = [];
      portalStore.clearTaskMilestones();
      portalStore.loadProjectTasks(recordName as string);
    } else if (routeName === "RecordDetail" && doctype === "Task" && recordName) {
      portalStore.clearProjectTasks();
      expandedTaskNames.value = [];
      portalStore.loadTaskMilestones(recordName as string);
    } else {
      portalStore.clearProjectTasks();
      portalStore.clearTaskMilestones();
      expandedTaskNames.value = [];
    }
  },
  { immediate: true }
);
</script>

<template>
  <Popover placement="bottom-end">
    <template #target="{ togglePopover }">
      <button
        class="flex items-center gap-1 px-2.5 py-1 text-xs text-ink-gray-6 border border-outline-gray-modals rounded hover:bg-surface-gray-2 transition-colors"
        @click="togglePopover"
      >
        <FeatherIcon name="columns" class="w-3.5 h-3.5" />
        Columns
      </button>
    </template>

    <template #body>
      <div class="my-2 rounded-lg border border-outline-gray-modals bg-surface-white shadow-xl">
        <div class="p-1.5 min-w-[200px]">
          <!-- Active columns list -->
          <div
            v-for="col in localColumns"
            :key="col.key"
            class="flex items-center justify-between gap-4 rounded px-2 py-1.5 text-sm text-ink-gray-8 hover:bg-surface-gray-2 cursor-default"
          >
            <div class="flex items-center gap-2">
              <FeatherIcon name="more-vertical" class="w-3.5 h-3.5 text-ink-gray-4 flex-shrink-0" />
              <span>{{ col.label }}</span>
            </div>
            <button
              class="text-ink-gray-3 hover:text-red-500 transition-colors flex-shrink-0"
              :disabled="localColumns.length <= 1"
              @click="removeColumn(col.key)"
            >
              <FeatherIcon name="x" class="w-3.5 h-3.5" />
            </button>
          </div>

          <!-- Footer: Add Column + Reset -->
          <div class="mt-1.5 flex flex-col gap-1 border-t border-outline-gray-modals pt-1.5">
            <Autocomplete
              :options="addableFields"
              :placeholder="'Column name'"
              @update:modelValue="addColumn"
            >
              <template #target="{ togglePopover }">
                <button
                  class="w-full flex items-center gap-1.5 text-xs text-ink-gray-5 hover:text-ink-gray-9 px-2 py-1.5 rounded hover:bg-surface-gray-2 transition-colors justify-start"
                  @click="togglePopover"
                >
                  <FeatherIcon name="plus" class="w-3.5 h-3.5" />
                  Add Column
                </button>
              </template>
            </Autocomplete>
            <button
              class="w-full flex items-center gap-1.5 text-xs text-ink-gray-5 hover:text-ink-gray-9 px-2 py-1.5 rounded hover:bg-surface-gray-2 transition-colors justify-start"
              @click="resetToDefault"
            >
              <FeatherIcon name="rotate-ccw" class="w-3.5 h-3.5" />
              Reset to Default
            </button>
          </div>
        </div>
      </div>
    </template>
  </Popover>
</template>

<script setup lang="ts">
import { Autocomplete, FeatherIcon, Popover } from "frappe-ui";
import { computed, ref, watch } from "vue";

interface Column { key: string; label: string; width?: string }
interface Field { label: string; value: string; fieldtype?: string }

const props = defineProps<{
  columns: Column[];
  allFields: Field[];
  defaultColumns: Column[];
}>();
const emit = defineEmits<{ (e: "update:columns", columns: Column[]): void }>();

const localColumns = ref<Column[]>([...props.columns]);

watch(() => props.columns, (val) => { localColumns.value = [...val]; }, { deep: true });

const addableFields = computed(() =>
  props.allFields
    .filter((f) => !localColumns.value.find((c) => c.key === f.value))
    .map((f) => ({ label: f.label, value: f.value }))
);

function removeColumn(key: string) {
  if (localColumns.value.length <= 1) return;
  localColumns.value = localColumns.value.filter((c) => c.key !== key);
  emit("update:columns", [...localColumns.value]);
}

function addColumn(option: any) {
  if (!option) return;
  if (localColumns.value.find((c) => c.key === option.value)) return;
  localColumns.value.push({ key: option.value, label: option.label, width: "10rem" });
  emit("update:columns", [...localColumns.value]);
}

function resetToDefault() {
  localColumns.value = [...props.defaultColumns];
  emit("update:columns", [...localColumns.value]);
}
</script>

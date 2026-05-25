<template>
  <Popover placement="bottom-end">
    <template #target="{ togglePopover }">
      <div class="flex items-center">
        <button
          class="flex items-center gap-1 px-2.5 py-1 text-xs border transition-colors"
          :class="activeFilters.length
            ? 'bg-blue-50 text-blue-700 border-blue-300 font-medium rounded-l'
            : 'text-ink-gray-6 border-outline-gray-modals hover:bg-surface-gray-2 rounded'"
          @click="togglePopover"
        >
          <FeatherIcon name="filter" class="w-3.5 h-3.5" />
          <span class="hidden sm:inline">Filter</span>
          <span
            v-if="activeFilters.length"
            class="flex h-4 w-4 items-center justify-center rounded bg-blue-600 text-white text-[10px] font-bold"
          >{{ activeFilters.length }}</span>
        </button>
        <button
          v-if="activeFilters.length"
          class="flex items-center justify-center w-6 h-[26px] text-blue-700 bg-blue-50 border border-blue-300 border-l-0 rounded-r hover:bg-blue-100 transition-colors"
          title="Clear filters"
          @click.stop="clearAll"
        >
          <FeatherIcon name="x" class="w-3 h-3" />
        </button>
      </div>
    </template>

    <template #body="{ close }">
      <div class="my-2 rounded-lg border border-outline-gray-modals bg-surface-white shadow-xl">
        <div class="p-2 min-w-[340px] sm:min-w-[420px]">

          <!-- Active filters -->
          <div v-if="activeFilters.length" class="mb-3 space-y-2.5">
            <div
              v-for="(f, i) in activeFilters"
              :key="i"
              class="flex items-center gap-2"
            >
              <span class="w-10 text-right text-sm text-ink-gray-5 flex-shrink-0">
                {{ i === 0 ? 'Where' : 'And' }}
              </span>
              <!-- Field label (read-only) -->
              <div class="min-w-[110px] px-2 py-1 border border-outline-gray-modals rounded text-xs text-ink-gray-7 bg-surface-gray-1 truncate">
                {{ f.fieldLabel }}
              </div>
              <!-- Operator -->
              <select
                v-model="f.operator"
                class="text-xs border border-outline-gray-modals rounded px-1.5 py-1 bg-surface-white text-ink-gray-7 focus:outline-none focus:ring-1 focus:ring-blue-400"
                @change="emitFilters"
              >
                <option v-for="op in getOperators(f.fieldtype)" :key="op.value" :value="op.value">{{ op.label }}</option>
              </select>
              <!-- Value -->
              <div class="flex-1 min-w-0">
                <select
                  v-if="f.fieldtype === 'Select' && f.fieldOptions"
                  v-model="f.value"
                  class="w-full text-xs border border-outline-gray-modals rounded px-1.5 py-1 bg-surface-white text-ink-gray-7 focus:outline-none focus:ring-1 focus:ring-blue-400"
                  @change="emitFilters"
                >
                  <option value=""></option>
                  <option v-for="opt in f.fieldOptions.split('\n').filter(Boolean)" :key="opt" :value="opt">{{ opt }}</option>
                </select>
                <input
                  v-else
                  v-model="f.value"
                  :type="['Int','Float','Currency'].includes(f.fieldtype) ? 'number' : 'text'"
                  class="w-full text-xs border border-outline-gray-modals rounded px-1.5 py-1 bg-surface-white text-ink-gray-9 focus:outline-none focus:ring-1 focus:ring-blue-400"
                  @input="debouncedEmit"
                />
              </div>
              <!-- Remove -->
              <button class="text-ink-gray-4 hover:text-red-500 flex-shrink-0" @click="removeFilter(i)">
                <FeatherIcon name="x" class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <!-- Empty state -->
          <div v-else class="mb-3 h-7 flex items-center px-3 text-sm text-ink-gray-5">
            Empty - Choose a field to filter by
          </div>

          <!-- Footer: Add Filter + Clear -->
          <div class="flex items-center justify-between">
            <Autocomplete
              :options="fieldOptions"
              :placeholder="'Field name'"
              @update:modelValue="addFilter"
            >
              <template #target="{ togglePopover }">
                <button
                  class="flex items-center gap-1.5 text-xs text-ink-gray-5 hover:text-ink-gray-9 px-2 py-1 rounded hover:bg-surface-gray-2 transition-colors"
                  @click="togglePopover"
                >
                  <FeatherIcon name="plus" class="w-3.5 h-3.5" />
                  Add Filter
                </button>
              </template>
            </Autocomplete>
            <button
              v-if="activeFilters.length"
              class="text-xs text-ink-gray-5 hover:text-ink-gray-9 px-2 py-1 rounded hover:bg-surface-gray-2 transition-colors"
              @click="() => { clearAll(); close(); }"
            >
              Clear all Filter
            </button>
          </div>
        </div>
      </div>
    </template>
  </Popover>
</template>

<script setup lang="ts">
import { Autocomplete, FeatherIcon, Popover } from "frappe-ui";
import { computed, ref } from "vue";

interface Field {
  label: string;
  value: string;
  fieldtype: string;
  options?: string;
}

interface ActiveFilter {
  fieldname: string;
  fieldLabel: string;
  fieldtype: string;
  fieldOptions: string;
  operator: string;
  value: string;
}

const props = defineProps<{ fields: Field[] }>();
const emit = defineEmits<{
  (e: "change", filters: Record<string, any>): void;
}>();

const activeFilters = ref<ActiveFilter[]>([]);

const fieldOptions = computed(() =>
  props.fields.map((f) => ({ label: f.label, value: f.value, fieldtype: f.fieldtype, options: f.options || "" }))
);

function getOperators(fieldtype: string) {
  const text = [
    { label: "Like", value: "like" },
    { label: "Not Like", value: "not like" },
    { label: "Equals", value: "=" },
    { label: "Not Equals", value: "!=" },
    { label: "Is Set", value: "is set" },
    { label: "Is Not Set", value: "is not set" },
  ];
  const num = [
    { label: "=", value: "=" },
    { label: "!=", value: "!=" },
    { label: ">", value: ">" },
    { label: "<", value: "<" },
    { label: ">=", value: ">=" },
    { label: "<=", value: "<=" },
  ];
  const sel = [
    { label: "Equals", value: "=" },
    { label: "Not Equals", value: "!=" },
    { label: "Is Set", value: "is set" },
    { label: "Is Not Set", value: "is not set" },
  ];
  if (["Int", "Float", "Currency", "Percent"].includes(fieldtype)) return num;
  if (fieldtype === "Select") return sel;
  if (["Date", "Datetime"].includes(fieldtype)) return [
    { label: "=", value: "=" },
    { label: "!=", value: "!=" },
    { label: ">", value: ">" },
    { label: "<", value: "<" },
    { label: ">=", value: ">=" },
    { label: "<=", value: "<=" },
    { label: "Is Set", value: "is set" },
  ];
  return text;
}

function defaultOperator(fieldtype: string): string {
  if (["Int", "Float", "Currency"].includes(fieldtype)) return "=";
  if (fieldtype === "Select") return "=";
  return "like";
}

function addFilter(option: any) {
  if (!option) return;
  const field = props.fields.find((f) => f.value === option.value);
  if (!field) return;
  activeFilters.value.push({
    fieldname: field.value,
    fieldLabel: field.label,
    fieldtype: field.fieldtype,
    fieldOptions: field.options || "",
    operator: defaultOperator(field.fieldtype),
    value: "",
  });
  emitFilters();
}

function removeFilter(i: number) {
  activeFilters.value.splice(i, 1);
  emitFilters();
}

function clearAll() {
  activeFilters.value = [];
  emitFilters();
}

function emitFilters() {
  const result: Record<string, any> = {};
  activeFilters.value.forEach((f) => {
    if (!f.value && !["is set", "is not set"].includes(f.operator)) return;
    if (f.operator === "is set") {
      result[f.fieldname] = ["is", "set"];
    } else if (f.operator === "is not set") {
      result[f.fieldname] = ["is", "not set"];
    } else if (f.operator === "like" || f.operator === "not like") {
      const v = f.value.includes("%") ? f.value : `%${f.value}%`;
      result[f.fieldname] = [f.operator.toUpperCase(), v];
    } else {
      result[f.fieldname] = [f.operator, f.value];
    }
  });
  emit("change", result);
}

let debounceTimer: ReturnType<typeof setTimeout> | null = null;
function debouncedEmit() {
  if (debounceTimer) clearTimeout(debounceTimer);
  debounceTimer = setTimeout(emitFilters, 400);
}
</script>

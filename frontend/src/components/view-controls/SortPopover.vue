<template>
  <!-- No sort yet: clicking opens Autocomplete directly -->
  <Autocomplete
    v-if="!currentSort"
    :options="fieldOptions"
    :placeholder="'Field name'"
    @update:modelValue="setSort"
  >
    <template #target="{ togglePopover }">
      <button
        class="flex items-center gap-1 px-2.5 py-1 text-xs text-ink-gray-6 border border-outline-gray-modals rounded hover:bg-surface-gray-2 transition-colors"
        @click="togglePopover"
      >
        <FeatherIcon name="arrow-up-down" class="w-3.5 h-3.5" />
        <span class="hidden sm:inline">Last Modified</span>
        <FeatherIcon name="chevron-down" class="w-3 h-3 hidden sm:inline" />
      </button>
    </template>
  </Autocomplete>

  <!-- Sort active: show popover with current sort -->
  <Popover v-else placement="bottom-end">
    <template #target="{ togglePopover }">
      <div class="flex items-center">
        <!-- Direction toggle -->
        <button
          class="flex items-center justify-center w-7 h-[26px] border border-r-0 border-outline-gray-modals rounded-l hover:bg-surface-gray-2 text-ink-gray-6 transition-colors"
          :title="currentSort.direction === 'asc' ? 'Ascending' : 'Descending'"
          @click.stop="toggleDirection"
        >
          <FeatherIcon :name="currentSort.direction === 'asc' ? 'arrow-up' : 'arrow-down'" class="w-3.5 h-3.5" />
        </button>
        <!-- Label -->
        <button
          class="flex items-center gap-1 px-2.5 py-1 text-xs text-ink-gray-6 border border-outline-gray-modals rounded-r hover:bg-surface-gray-2 transition-colors"
          @click="togglePopover"
        >
          <span class="hidden sm:inline">{{ sortLabel }}</span>
          <FeatherIcon name="chevron-down" class="w-3 h-3 hidden sm:inline" />
        </button>
      </div>
    </template>

    <template #body="{ close }">
      <div class="my-2 rounded-lg border border-outline-gray-modals bg-surface-white shadow-xl">
        <div class="p-2 min-w-[260px]">
          <!-- Current sort row -->
          <div class="mb-3 flex items-center gap-2">
            <span class="w-6 h-6 flex items-center justify-center text-ink-gray-4 flex-shrink-0 cursor-grab">
              <FeatherIcon name="more-vertical" class="w-3.5 h-3.5" />
            </span>
            <div class="flex flex-1 items-center">
              <!-- direction toggle -->
              <button
                class="flex items-center justify-center w-7 h-7 border border-r-0 border-outline-gray-modals rounded-l hover:bg-surface-gray-2 text-ink-gray-6 transition-colors text-xs"
                @click="toggleDirection"
              >
                <FeatherIcon :name="currentSort.direction === 'asc' ? 'arrow-up' : 'arrow-down'" class="w-3.5 h-3.5" />
              </button>
              <!-- field label -->
              <Autocomplete
                :options="fieldOptions"
                :placeholder="'Field'"
                @update:modelValue="changeSort"
              >
                <template #target="{ togglePopover }">
                  <button
                    class="flex items-center justify-between gap-2 flex-1 px-2.5 py-1 text-xs border border-outline-gray-modals rounded-r hover:bg-surface-gray-2 text-ink-gray-7 transition-colors"
                    @click="togglePopover"
                  >
                    {{ sortLabel }}
                    <FeatherIcon name="chevron-down" class="w-3 h-3 text-ink-gray-4" />
                  </button>
                </template>
              </Autocomplete>
            </div>
            <button class="text-ink-gray-4 hover:text-red-500 flex-shrink-0" @click="() => { clearSort(); close(); }">
              <FeatherIcon name="x" class="w-3.5 h-3.5" />
            </button>
          </div>

          <!-- Footer -->
          <div class="flex items-center justify-between border-t border-outline-gray-modals pt-2">
            <Autocomplete
              :options="fieldOptions"
              :placeholder="'Field name'"
              @update:modelValue="setSort"
            >
              <template #target="{ togglePopover }">
                <button
                  class="flex items-center gap-1.5 text-xs text-ink-gray-5 hover:text-ink-gray-9 px-2 py-1 rounded hover:bg-surface-gray-2 transition-colors"
                  @click="togglePopover"
                >
                  <FeatherIcon name="plus" class="w-3.5 h-3.5" />
                  Add Sort
                </button>
              </template>
            </Autocomplete>
            <button
              class="text-xs text-ink-gray-5 hover:text-ink-gray-9 px-2 py-1 rounded hover:bg-surface-gray-2 transition-colors"
              @click="() => { clearSort(); close(); }"
            >
              Clear Sort
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

interface Field { label: string; value: string; fieldtype: string }

const props = defineProps<{ fields: Field[] }>();
const emit = defineEmits<{ (e: "change", orderBy: string): void }>();

interface SortState { fieldname: string; direction: "asc" | "desc" }

const currentSort = ref<SortState | null>({ fieldname: "modified", direction: "desc" });

const fieldOptions = computed(() =>
  props.fields.map((f) => ({ label: f.label, value: f.value }))
);

const sortLabel = computed(() => {
  if (!currentSort.value) return "Sort";
  const field = props.fields.find((f) => f.value === currentSort.value!.fieldname);
  return field?.label || currentSort.value.fieldname;
});

function setSort(option: any) {
  if (!option) return;
  currentSort.value = { fieldname: option.value, direction: "asc" };
  emitSort();
}

function changeSort(option: any) {
  if (!option || !currentSort.value) return;
  currentSort.value = { ...currentSort.value, fieldname: option.value };
  emitSort();
}

function toggleDirection() {
  if (!currentSort.value) return;
  currentSort.value.direction = currentSort.value.direction === "asc" ? "desc" : "asc";
  emitSort();
}

function clearSort() {
  currentSort.value = null;
  emit("change", "modified desc");
}

function emitSort() {
  if (!currentSort.value) return;
  emit("change", `${currentSort.value.fieldname} ${currentSort.value.direction}`);
}
</script>

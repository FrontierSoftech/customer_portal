<template>
  <div class="flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center gap-3 px-6 py-4 border-b border-outline-gray-modals bg-surface-white">
      <button
        class="text-ink-gray-5 hover:text-ink-gray-9"
        @click="router.back()"
      >
        <FeatherIcon name="arrow-left" class="w-4 h-4" />
      </button>
      <div>
        <h1 class="text-lg font-semibold text-ink-gray-9">
          {{ recordTitle || name }}
        </h1>
        <span class="text-xs text-ink-gray-5">{{ config?.label || doctypeName }} · {{ name }}</span>
      </div>
      <div class="ml-auto flex items-center gap-2">
        <span
          v-if="recordStatus"
          class="inline-flex items-center px-2.5 py-1 rounded-full text-xs bg-surface-gray-2 text-ink-gray-7 font-medium"
        >
          {{ recordStatus }}
        </span>
        <button
          v-if="isQuotation"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-ink-gray-7 border border-outline-gray-modals rounded-md hover:bg-surface-gray-1 transition-colors"
          @click="viewPdf"
        >
          <FeatherIcon name="file-text" class="w-3.5 h-3.5" />
          View PDF
        </button>
      </div>
    </div>

    <!-- Quotation approval banner -->
    <div v-if="isQuotation && doc.customer_approval" class="px-6 py-3 border-b border-outline-gray-modals flex items-center gap-2 text-sm font-medium"
      :class="doc.customer_approval === 'Approved'
        ? 'bg-green-50 text-green-800 border-green-200'
        : 'bg-red-50 text-red-800 border-red-200'"
    >
      <FeatherIcon :name="doc.customer_approval === 'Approved' ? 'check-circle' : 'x-circle'" class="w-4 h-4 flex-shrink-0" />
      <span>You {{ doc.customer_approval === 'Approved' ? 'approved' : 'rejected' }} this quotation</span>
      <span v-if="doc.customer_approval_date" class="opacity-60 font-normal ml-1">· {{ formatDate(doc.customer_approval_date) }}</span>
      <span v-if="doc.customer_approval_remarks" class="ml-2 font-normal opacity-80">— "{{ doc.customer_approval_remarks }}"</span>
    </div>

    <!-- Quotation approve / reject action bar -->
    <div v-if="isQuotation && !doc.customer_approval && doc.docstatus !== 2" class="px-6 py-3 border-b border-outline-gray-modals bg-amber-50 flex items-center gap-3">
      <FeatherIcon name="info" class="w-4 h-4 text-amber-600 flex-shrink-0" />
      <span class="text-sm text-amber-800 flex-1">Please review this quotation and let us know your decision.</span>
      <button
        class="px-4 py-1.5 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 font-medium flex items-center gap-1.5"
        @click="handleApprove"
      >
        <FeatherIcon name="check" class="w-3.5 h-3.5" /> Approve
      </button>
      <button
        class="px-4 py-1.5 bg-red-600 text-white text-sm rounded-md hover:bg-red-700 font-medium flex items-center gap-1.5"
        @click="showRejectModal = true"
      >
        <FeatherIcon name="x" class="w-3.5 h-3.5" /> Reject
      </button>
    </div>

    <!-- Communication thread -->
    <div ref="threadEl" class="flex-1 overflow-y-auto px-6 py-4 space-y-4">
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else-if="communications.length === 0" class="text-center py-8 text-ink-gray-5 text-sm">
        No messages yet. Send a message below to start a conversation.
      </div>
      <div
        v-for="comm in communications"
        :key="comm.name"
        class="flex gap-3"
        :class="comm.sender === authStore.user ? 'flex-row-reverse' : ''"
      >
        <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
          <span class="text-blue-700 text-xs font-semibold">
            {{ (comm.sender || '?').charAt(0).toUpperCase() }}
          </span>
        </div>
        <div
          class="max-w-lg rounded-lg px-4 py-2.5 text-sm"
          :class="comm.sender === authStore.user
            ? 'bg-blue-600 text-white'
            : 'bg-surface-gray-1 text-ink-gray-9 border border-outline-gray-modals'"
        >
          <div class="font-medium text-xs mb-1 opacity-70">{{ comm.sender }}</div>
          <div v-html="comm.content"></div>

          <!-- Attachments in message -->
          <div v-if="comm.attachments && comm.attachments.length" class="mt-2 space-y-1">
            <a
              v-for="att in comm.attachments"
              :key="att.file_url"
              :href="att.file_url"
              target="_blank"
              class="flex items-center gap-1.5 text-xs underline opacity-80 hover:opacity-100"
            >
              <FeatherIcon name="paperclip" class="w-3 h-3 flex-shrink-0" />
              {{ att.file_name }}
              <span v-if="att.file_size" class="opacity-60">({{ formatSize(att.file_size) }})</span>
            </a>
          </div>

          <div class="text-xs mt-1 opacity-60">{{ formatDate(comm.creation) }}</div>
        </div>
      </div>
    </div>

    <!-- Reply box -->
    <div class="border-t border-outline-gray-modals px-6 py-4 bg-surface-white">
      <div class="border border-outline-gray-modals rounded-lg overflow-hidden">
        <textarea
          v-model="replyContent"
          placeholder="Type a message..."
          rows="3"
          class="w-full px-4 py-3 text-sm text-ink-gray-9 bg-surface-white resize-none focus:outline-none"
        ></textarea>

        <!-- Selected files preview -->
        <div v-if="selectedFiles.length" class="px-4 py-2 border-t border-outline-gray-modals flex flex-wrap gap-2">
          <div
            v-for="(f, i) in selectedFiles"
            :key="i"
            class="flex items-center gap-1.5 px-2 py-1 bg-surface-gray-2 rounded text-xs text-ink-gray-7"
          >
            <FeatherIcon name="paperclip" class="w-3 h-3 flex-shrink-0" />
            <span class="max-w-[160px] truncate">{{ f.name }}</span>
            <button @click="removeFile(i)" class="text-ink-gray-4 hover:text-red-500 ml-1">
              <FeatherIcon name="x" class="w-3 h-3" />
            </button>
          </div>
        </div>

        <div class="flex items-center justify-between px-4 py-2 bg-surface-gray-1 border-t border-outline-gray-modals">
          <!-- Attach button -->
          <label class="cursor-pointer text-ink-gray-5 hover:text-ink-gray-9 flex items-center gap-1.5 text-xs">
            <FeatherIcon name="paperclip" class="w-4 h-4" />
            <span>Attach</span>
            <input
              ref="fileInputEl"
              type="file"
              multiple
              class="hidden"
              @change="onFilesSelected"
            />
          </label>

          <button
            class="px-4 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            :disabled="(!replyContent.trim() && !selectedFiles.length) || sending"
            @click="sendReply"
          >
            {{ sending ? (uploadProgress || 'Sending...') : 'Send' }}
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- PDF Viewer Modal -->
  <div v-if="showPdfModal" class="fixed inset-0 z-50 flex flex-col bg-white">
    <!-- PDF viewer header -->
    <div class="flex items-center gap-3 px-4 py-3 border-b border-outline-gray-modals bg-surface-white flex-shrink-0">
      <button
        class="text-ink-gray-5 hover:text-ink-gray-9 p-1 -ml-1 rounded"
        @click="showPdfModal = false"
      >
        <FeatherIcon name="arrow-left" class="w-5 h-5" />
      </button>
      <div class="flex-1 min-w-0">
        <div class="text-sm font-semibold text-ink-gray-9 truncate">{{ name }}</div>
        <div class="text-xs text-ink-gray-5">Quotation PDF</div>
      </div>
      <a
        :href="pdfUrl"
        download
        class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-ink-gray-7 border border-outline-gray-modals rounded-md hover:bg-surface-gray-1 transition-colors flex-shrink-0"
      >
        <FeatherIcon name="download" class="w-3.5 h-3.5" />
        <span class="hidden sm:inline">Download</span>
      </a>
    </div>

    <!-- PDF iframe — desktop + Android Chrome -->
    <iframe
      :src="pdfUrl"
      class="flex-1 w-full border-none hidden sm:block"
      style="background:#f3f4f6"
    />

    <!-- Mobile: full-height embed attempt + fallback button -->
    <div class="flex-1 flex flex-col sm:hidden overflow-hidden">
      <object
        :data="pdfUrl"
        type="application/pdf"
        class="flex-1 w-full"
        style="min-height:0"
      >
        <!-- iOS Safari fallback — object/iframe won't render PDF inline -->
        <div class="flex flex-col items-center justify-center h-full gap-4 p-6 text-center">
          <FeatherIcon name="file-text" class="w-12 h-12 text-ink-gray-3" />
          <p class="text-sm text-ink-gray-6">Your browser cannot display the PDF inline.</p>
          <a
            :href="pdfUrl"
            target="_blank"
            class="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700"
          >
            <FeatherIcon name="external-link" class="w-4 h-4" />
            Open PDF
          </a>
        </div>
      </object>
    </div>
  </div>

  <!-- Reject modal -->
  <div v-if="showRejectModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
    <div class="bg-surface-white rounded-xl shadow-xl w-full max-w-md mx-4 overflow-hidden">
      <div class="px-6 py-4 border-b border-outline-gray-modals flex items-center justify-between">
        <h2 class="text-base font-semibold text-ink-gray-9">Reject Quotation</h2>
        <button @click="showRejectModal = false" class="text-ink-gray-4 hover:text-ink-gray-9">
          <FeatherIcon name="x" class="w-4 h-4" />
        </button>
      </div>
      <div class="px-6 py-4">
        <label class="block text-sm text-ink-gray-7 mb-1">Reason <span class="text-ink-gray-4">(optional)</span></label>
        <textarea
          v-model="rejectRemarks"
          placeholder="Let us know why you are rejecting this quotation..."
          rows="3"
          class="w-full border border-outline-gray-modals rounded-lg px-3 py-2 text-sm text-ink-gray-9 focus:outline-none focus:ring-2 focus:ring-red-400 resize-none"
        ></textarea>
      </div>
      <div class="px-6 py-4 border-t border-outline-gray-modals flex justify-end gap-3">
        <button
          class="px-4 py-1.5 text-sm text-ink-gray-7 hover:text-ink-gray-9"
          @click="showRejectModal = false"
        >Cancel</button>
        <button
          class="px-4 py-1.5 bg-red-600 text-white text-sm rounded-md hover:bg-red-700 font-medium flex items-center gap-1.5"
          :disabled="actioning"
          @click="handleReject"
        >
          <FeatherIcon name="x" class="w-3.5 h-3.5" />
          {{ actioning ? 'Rejecting...' : 'Confirm Reject' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { call, FeatherIcon } from "frappe-ui";
import { computed, nextTick, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { usePortalStore } from "../stores/portal";
import { useAuthStore } from "../stores/auth";

const props = defineProps<{ doctypeName: string; name: string }>();
const router = useRouter();
const portalStore = usePortalStore();
const authStore = useAuthStore();

const loading = ref(false);
const sending = ref(false);
const actioning = ref(false);
const uploadProgress = ref("");
const communications = ref<any[]>([]);
const doc = ref<any>({});
const replyContent = ref("");
const selectedFiles = ref<File[]>([]);
const fileInputEl = ref<HTMLInputElement | null>(null);
const threadEl = ref<HTMLElement | null>(null);
const showRejectModal = ref(false);
const rejectRemarks = ref("");
const showPdfModal = ref(false);

const config = computed(() =>
  portalStore.doctypes.find((d) => d.doctype_name === props.doctypeName)
);

const recordTitle = computed(() => {
  const tf = config.value?.title_field;
  return tf ? doc.value[tf] : doc.value.name;
});

const recordStatus = computed(() => {
  const sf = config.value?.status_field;
  return sf ? doc.value[sf] : null;
});

const isQuotation = computed(() => props.doctypeName === "Quotation");

const pdfUrl = computed(() =>
  `/api/method/customer_portal.api.portal.download_quotation_pdf?name=${encodeURIComponent(props.name)}`
);

function onFilesSelected(e: Event) {
  const input = e.target as HTMLInputElement;
  if (!input.files) return;
  selectedFiles.value.push(...Array.from(input.files));
  input.value = "";
}

function removeFile(index: number) {
  selectedFiles.value.splice(index, 1);
}

function getCsrfToken(): string {
  return (window as any).csrf_token || "";
}

async function uploadFile(file: File): Promise<string> {
  const form = new FormData();
  form.append("file", file, file.name);
  form.append("is_private", "0");
  form.append("folder", "Home/Attachments");

  const res = await fetch("/api/method/upload_file", {
    method: "POST",
    headers: { "X-Frappe-CSRF-Token": getCsrfToken() },
    credentials: "include",
    body: form,
  });

  if (!res.ok) throw new Error(`Upload failed: ${file.name}`);
  const data = await res.json();
  return data.message.file_url as string;
}

async function fetchRecord() {
  loading.value = true;
  try {
    await portalStore.load();
    const res = await call("customer_portal.api.portal.get_record", {
      doctype_name: props.doctypeName,
      name: props.name,
    });
    doc.value = res.doc || {};
    communications.value = res.communications || [];

    await nextTick();
    scrollToBottom();
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
}

async function sendReply() {
  if ((!replyContent.value.trim() && !selectedFiles.value.length) || sending.value) return;
  sending.value = true;

  try {
    // Upload files first
    const fileUrls: string[] = [];
    if (selectedFiles.value.length) {
      for (let i = 0; i < selectedFiles.value.length; i++) {
        uploadProgress.value = `Uploading ${i + 1}/${selectedFiles.value.length}...`;
        const url = await uploadFile(selectedFiles.value[i]);
        fileUrls.push(url);
      }
    }

    uploadProgress.value = "";
    await call("customer_portal.api.portal.send_reply", {
      doctype_name: props.doctypeName,
      name: props.name,
      message: replyContent.value || " ",
      attachments: fileUrls.length ? JSON.stringify(fileUrls) : null,
    });

    replyContent.value = "";
    selectedFiles.value = [];
    await fetchRecord();
  } catch (e) {
    console.error(e);
  } finally {
    sending.value = false;
    uploadProgress.value = "";
  }
}

function viewPdf() {
  showPdfModal.value = true;
}

async function handleApprove() {
  if (actioning.value) return;
  actioning.value = true;
  try {
    await call("customer_portal.api.portal.quotation_action", {
      name: props.name,
      action: "Approved",
    });
    await fetchRecord();
  } catch (e) {
    console.error(e);
  } finally {
    actioning.value = false;
  }
}

async function handleReject() {
  if (actioning.value) return;
  actioning.value = true;
  try {
    await call("customer_portal.api.portal.quotation_action", {
      name: props.name,
      action: "Rejected",
      remarks: rejectRemarks.value,
    });
    showRejectModal.value = false;
    rejectRemarks.value = "";
    await fetchRecord();
  } catch (e) {
    console.error(e);
  } finally {
    actioning.value = false;
  }
}

function scrollToBottom() {
  if (threadEl.value) {
    threadEl.value.scrollTop = threadEl.value.scrollHeight;
  }
}

function formatDate(d: string) {
  if (!d) return "";
  return new Date(d).toLocaleString(undefined, {
    year: "numeric", month: "short", day: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

onMounted(fetchRecord);
</script>

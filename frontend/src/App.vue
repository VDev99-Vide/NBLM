<template>
  <div class="flex h-screen w-full overflow-hidden">
    <aside class="w-64 flex-shrink-0 border-r border-white/5 bg-surface-raised/50 backdrop-blur-xl flex flex-col">
      <div class="p-4 border-b border-white/5">
        <h1 class="text-lg font-bold text-white flex items-center gap-2"><span class="text-2xl">📒</span> NBLM</h1>
        <p class="text-xs text-gray-500 mt-1">Quản Gia AI Cá Nhân</p>
      </div>
      <nav class="flex-1 overflow-y-auto p-3 space-y-1">
        <div class="text-xs font-medium text-gray-500 uppercase tracking-wider px-2 py-2">Notebooks</div>
        <button v-for="nb in notebooks" :key="nb.id" @click="activeNb=nb.id; loadEntries(nb.id)"
          class="w-full text-left px-3 py-2 rounded-lg text-sm transition-all"
          :class="activeNb===nb.id?'bg-accent/20 text-white':'text-gray-400 hover:bg-white/5 hover:text-gray-200'">
          {{ nb.icon || '📓' }} {{ nb.name }}
        </button>
      </nav>
      <div class="p-3 border-t border-white/5">
        <button @click="showCredentials=!showCredentials" class="w-full text-left px-3 py-2 rounded-lg text-sm text-gray-400 hover:bg-white/5">
          🔑 Credentials
        </button>
      </div>
    </aside>
    <main class="flex-1 flex flex-col min-w-0">
      <div class="flex-1 overflow-y-auto p-6 space-y-4" ref="chatContainer">
        <div v-for="msg in messages" :key="msg.id" class="flex" :class="msg.role==='user'?'justify-end':'justify-start'">
          <div class="max-w-2xl px-4 py-3" :class="msg.role==='user'?'chat-bubble-user':'chat-bubble-ai'">
            <img v-if="msg.image" :src="msg.image" class="max-w-xs rounded-lg mb-2 border border-white/10"/>
            <p class="whitespace-pre-wrap">{{ msg.text }}</p>
          </div>
        </div>
        <div v-if="loading" class="flex justify-start"><div class="chat-bubble-ai px-4 py-3 animate-pulse">Đang suy nghĩ...</div></div>
      </div>
      <div class="p-4 border-t border-white/5">
        <div v-if="previewImage" class="mb-2 relative inline-block">
          <img :src="previewImage" class="h-16 rounded border border-white/10"/>
          <button @click="previewImage=null" class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 text-xs">✕</button>
        </div>
        <form @submit.prevent="sendMessage" class="flex gap-3">
          <label class="flex items-center justify-center w-12 h-12 rounded-xl bg-white/5 border border-white/10 cursor-pointer hover:bg-white/10 transition-all">
            📷<input type="file" accept="image/*" class="hidden" @change="onFileSelect"/>
          </label>
          <input v-model="inputMsg" type="text" placeholder="Hỏi Quản Gia..." class="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-accent/50"/>
          <button type="submit" :disabled="(!inputMsg.trim()&&!previewImage)||loading" class="bg-accent hover:bg-accent-hover disabled:opacity-50 text-white px-6 py-3 rounded-xl font-medium transition-all">Gửi</button>
        </form>
      </div>
    </main>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'

const API_BASE = import.meta.env.VITE_API_URL || ''
const notebooks = ref<any[]>([])
const activeNb = ref('')
const messages = ref<{id:string;role:string;text:string;image?:string}[]>([{id:'welcome',role:'assistant',text:'Chào anh! Em là Quản Gia NBLM. Anh cần em giúp gì?'}])
const inputMsg = ref('')
const loading = ref(false)
const previewImage = ref<string|null>(null)
const selectedFile = ref<File|null>(null)
const showCredentials = ref(false)
const chatContainer = ref<HTMLElement>()

async function onFileSelect(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  selectedFile.value = file
  previewImage.value = URL.createObjectURL(file)
}

async function sendMessage() {
  const txt = inputMsg.value.trim()
  const file = selectedFile.value
  if ((!txt && !file) || loading.value) return
  const qid = Date.now().toString()
  let imageUrl: string | undefined
  if (file) {
    messages.value.push({id:qid,role:'user',text:txt||'(ảnh)',image:previewImage.value||undefined})
    try {
      const fd = new FormData(); fd.append('file', file)
      const upRes = await fetch(`${API_BASE}/api/upload`,{method:'POST',body:fd})
      const upData = await upRes.json()
      imageUrl = upData.public_url || upData.r2_key
    } catch(e) { console.error('Upload failed',e) }
  } else {
    messages.value.push({id:qid,role:'user',text:txt})
  }
  inputMsg.value = ''; previewImage.value = null; selectedFile.value = null
  loading.value = true
  await nextTick(); chatContainer.value?.scrollTo({top:chatContainer.value.scrollHeight,behavior:'smooth'})
  try {
    const payload: any = {message: txt || 'Phân tích ảnh này giúp anh', history: messages.value.slice(-10).map(m=>({role:m.role,content:m.text}))}
    if (imageUrl) payload.image_url = imageUrl
    const res = await fetch(`${API_BASE}/api/chat`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})
    const data = await res.json()
    messages.value.push({id:`a-${qid}`,role:'assistant',text:data.answer||'Em chưa có câu trả lời.'})
  } catch(e) {
    messages.value.push({id:`e-${qid}`,role:'assistant',text:'Lỗi kết nối backend. Kiểm tra lại API URL.'})
  } finally { loading.value = false; await nextTick(); chatContainer.value?.scrollTo({top:chatContainer.value.scrollHeight,behavior:'smooth'}) }
}

async function loadEntries(nbId: string) {
  try { const r = await fetch(`${API_BASE}/api/entries?notebook_id=${nbId}`); /* future: display entries */ } catch(e){}
}

onMounted(async()=>{
  try { const r=await fetch(`${API_BASE}/api/notebooks`); notebooks.value=await r.json(); if(notebooks.value.length) { activeNb.value=notebooks.value[0].id; loadEntries(activeNb.value) } } catch(e){console.error(e)}
})
</script>

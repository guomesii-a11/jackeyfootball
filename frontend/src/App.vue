<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import SideNav from '@/components/SideNav.vue'
import LangSwitch from '@/components/LangSwitch.vue'

const { t } = useI18n()
</script>

<template>
  <div class="relative min-h-screen text-ink flex flex-col">
    <!-- 背景光晕 -->
    <div class="bg-glow" style="width:480px;height:480px;background:#FF5A36;top:-120px;left:-80px"></div>
    <div class="bg-glow" style="width:520px;height:520px;background:#1FB6C9;bottom:-160px;right:-100px;animation-delay:-5s"></div>
    <div class="bg-glow" style="width:360px;height:360px;background:#9B59F6;top:40%;left:55%;opacity:.22;animation-delay:-9s"></div>

    <!-- 顶部导航 -->
    <header class="fixed top-0 inset-x-0 z-20 glass rounded-none border-x-0 border-t-0">
      <div class="flex items-center gap-6 px-6 py-4">
        <RouterLink to="/" class="flex items-center gap-2 font-extrabold text-2xl no-underline">
          <span class="text-2xl">⚽</span>
          <span class="bg-gradient-to-r from-forward to-gold bg-clip-text text-transparent">JackeyFootball</span>
        </RouterLink>
        <div class="ml-auto"><LangSwitch /></div>
      </div>
    </header>

    <div class="flex pt-[68px] flex-1">
      <SideNav class="hidden lg:flex w-[35%] shrink-0 p-6" />
      <main class="flex-1 min-w-0 p-6">
        <RouterView />
      </main>
    </div>

    <!-- 全局页脚 -->
    <footer class="glass rounded-none border-x-0 border-b-0 mt-auto py-3 px-6 text-center text-xs text-muted">
      {{ t('footer.disclaimer') }}
    </footer>
  </div>
</template>



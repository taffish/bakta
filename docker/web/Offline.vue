<template>
  <div class="page">
    <header class="container py-4 border-bottom mb-4">
      <p class="small text-secondary mb-1">TAFFISH · BAKTA · LOCAL RESULT VIEWER</p>
      <h1 class="h2">Explore a Bakta result</h1>
      <p class="mb-1">Official Bakta Web UI 1.4.0 viewing components, packaged for local use.</p>
      <p class="mb-0 text-secondary">No cloud submission or account. Files remain in this browser.
        DbXref links open external websites only when you choose them.</p>
    </header>
    <main>
      <p class="container small text-secondary">On narrow screens, scroll inside wide plots and tables to inspect all details.</p>
      <ShowOwnResultPage />
    </main>
    <footer class="container py-4 border-top small text-secondary">
      Viewer: Bakta Web, Beyvers et al. (2025), doi:10.1093/nar/gkaf335, GPL-3.0.
      Annotations are produced by Bakta, not by this viewer. Use bakta_io for CLI output conversion.
    </footer>
  </div>
</template>
<script setup lang="ts">
import ShowOwnResultPage from './pages/show-own-result-file/ShowOwnResultPage.vue'
</script>
<style>
/* Local shell presentation only; keep upstream parsing and plot calculations. */
.page .nav-tabs { flex-wrap: wrap; overflow: visible; }
.page .card { overflow-x: auto; }
.page .card > .w-100.h-100 > .my-2 { min-width: 600px; }
.page .accordion-body .d-flex { flex-wrap: wrap; gap: 1rem; }
.page .accordion-body .col { min-width: 14rem; }
</style>

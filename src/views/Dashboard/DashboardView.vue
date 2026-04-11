<template>
  <div class="p-8 bg-[#f8fafc] min-h-screen w-full">
    <header class="mb-8">
      <h1 class="text-2xl font-bold text-slate-800">Dashboard</h1>
      <p class="text-slate-500 text-sm">Visão geral das análises de segurança documental</p>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex justify-between items-center">
        <div>
          <p class="text-slate-500 text-xs font-semibold uppercase mb-1">Total de Análises</p>
          <p class="text-3xl font-bold text-slate-800">5</p>
        </div>
        <div class="bg-blue-50 p-3 rounded-xl text-blue-600 text-xl">📄</div>
      </div>
      
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex justify-between items-center">
        <div>
          <p class="text-slate-500 text-xs font-semibold uppercase mb-1">Aprovados</p>
          <p class="text-3xl font-bold text-slate-800">2</p>
        </div>
        <div class="bg-emerald-50 p-3 rounded-xl text-emerald-600 text-xl">✅</div>
      </div>

      <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex justify-between items-center">
        <div>
          <p class="text-slate-500 text-xs font-semibold uppercase mb-1">Rejeitados</p>
          <p class="text-3xl font-bold text-slate-800">2</p>
        </div>
        <div class="bg-rose-50 p-3 rounded-xl text-rose-600 text-xl">❌</div>
      </div>

      <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex justify-between items-center">
        <div>
          <p class="text-slate-500 text-xs font-semibold uppercase mb-1">Pendentes</p>
          <p class="text-3xl font-bold text-slate-800">1</p>
        </div>
        <div class="bg-amber-50 p-3 rounded-xl text-amber-600 text-xl">🕒</div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      
      <div class="lg:col-span-2 bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
        <div class="flex justify-between items-center mb-6">
          <h3 class="font-bold text-slate-800 text-lg">Últimas Análises</h3>
        </div>
        
        <div class="overflow-x-auto">
          <table class="w-full text-left">
            <thead>
              <tr class="text-slate-400 text-xs uppercase border-b border-slate-50">
                <th class="pb-4 font-medium">Protocolo / Documento</th>
                <th class="pb-4 font-medium">Status</th>
                <th class="pb-4 font-medium text-right">Data</th>
              </tr>
            </thead>
            <tbody class="text-sm">
              <tr class="border-b border-slate-50 last:border-0 group hover:bg-slate-50 transition">
                <td class="py-4">
                  <div class="font-bold text-slate-700">OS-MMWMH3RO</div>
                  <div class="text-xs text-slate-400 font-medium">Comprovante Escolaridade · Sergio Luiz</div>
                </td>
                <td class="py-4">
                  <span class="bg-rose-100 text-rose-600 px-3 py-1 rounded-full text-[10px] font-bold uppercase">Rejeitado</span>
                </td>
                <td class="py-4 text-right text-slate-400">18 mar</td>
              </tr>
              <tr class="border-b border-slate-50 last:border-0 group hover:bg-slate-50 transition">
                <td class="py-4">
                  <div class="font-bold text-slate-700">OS-P7Q8R9</div>
                  <div class="text-xs text-slate-400 font-medium">Histórico Escolar · Ana Oliveira</div>
                </td>
                <td class="py-4">
                  <span class="bg-slate-100 text-slate-500 px-3 py-1 rounded-full text-[10px] font-bold uppercase">Pendente</span>
                </td>
                <td class="py-4 text-right text-slate-400">18 mar</td>
              </tr>
              <tr class="border-b border-slate-50 last:border-0 group hover:bg-slate-50 transition">
                <td class="py-4">
                  <div class="font-bold text-slate-700">OS-X1Y2Z3</div>
                  <div class="text-xs text-slate-400 font-medium">Cert. Pós-Graduação · Carlos Pereira</div>
                </td>
                <td class="py-4">
                  <span class="bg-emerald-100 text-emerald-600 px-3 py-1 rounded-full text-[10px] font-bold uppercase">Aprovado</span>
                </td>
                <td class="py-4 text-right text-slate-400">18 mar</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col items-center">
        <h3 class="font-bold text-slate-800 text-lg self-start mb-6">Distribuição por Status</h3>
        
        <div class="relative w-40 h-40">
          <div class="w-full h-full rounded-full border-[12px] border-emerald-500 border-t-amber-400 border-r-rose-400"></div>
        </div>

        <div class="mt-8 flex flex-wrap justify-center gap-3 text-[10px] font-bold uppercase tracking-widest text-slate-400">
          <div class="flex items-center gap-1.5"><span class="w-2 h-2 bg-emerald-500 rounded-full"></span> Rejeitado</div>
          <div class="flex items-center gap-1.5"><span class="w-2 h-2 bg-rose-400 rounded-full"></span> Pendente</div>
          <div class="flex items-center gap-1.5"><span class="w-2 h-2 bg-amber-400 rounded-full"></span> Aprovado</div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
</script>
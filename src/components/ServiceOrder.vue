<template>
  <div class="min-h-screen bg-gray-50 p-8 text-slate-700">
    <div class="max-w-5xl mx-auto">
      <header class="mb-8">
        <h1 class="text-2xl font-bold text-slate-800">Ordens de serviço</h1>
        <p class="text-slate-500">Histórico completo de análises de documentos</p>
      </header>

      <div class="flex items-center gap-4 mb-6">
        <div class="flex-1">
          <div class="relative">
            <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
              <svg class="w-4 h-4 text-gray-400" viewBox="0 0 24 24" fill="none">
                <path stroke="currentColor" stroke-width="2" stroke-linecap="round" d="m21 21-3.5-3.5M17 10a7 7 0 1 1-14 0 7 7 0 0 1 14 0Z"/>
              </svg>
            </div>

            <input
              v-model="search"
              type="search"
              class="w-full p-3 pl-9 pr-28 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Buscar por OS ou solicitante"
            />

          </div>
        </div>

        <el-dropdown @command="handleStatus" trigger="click">
          <span class="cursor-pointer px-4 py-2 text-sm font-semibold bg-white border rounded-lg flex items-center gap-2 hover:bg-gray-50">
            {{ selectedStatus || 'Todos os status' }}
            <svg class="w-4 h-4 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
              <path d="M5.22 8.22a.75.75 0 0 1 1.06 0L10 11.94l3.72-3.72a.75.75 0 1 1 1.06 1.06l-4.25 4.25a.75.75 0 0 1-1.06 0L5.22 9.28a.75.75 0 0 1 0-1.06Z"/>
            </svg>
          </span>

          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="">Todos</el-dropdown-item>
              <el-dropdown-item
                v-for="status in statusList"
                :key="status"
                :command="status"
              >
                {{ status }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

      <table class="w-full bg-white rounded shadow">
        <thead>
          <tr class="text-xs text-gray-500 uppercase">
            <th class="px-4 py-3 text-left">Nº OS</th>
            <th class="px-4 py-3 text-left">Solicitante</th>
            <th class="px-4 py-3 text-left">Tipo</th>
            <th class="px-4 py-3 text-left">Status</th>
            <th class="px-4 py-3 text-left">Veredito</th>
            <th class="px-4 py-3 text-left">Data</th>
            <th class="px-4 py-3 text-left">Ações</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="item in filteredList" :key="item.id" class="border-t">
            <td class="px-4 py-3">{{ item.id }}</td>
            <td class="px-4 py-3">{{ item.nome }}</td>
            <td class="px-4 py-3">{{ item.tipo }}</td>

            <td class="px-4 py-3">
              <span :class="statusClass(item.status)">
                {{ item.status }}
              </span>
            </td>

            <td class="px-4 py-3">
              <span :class="vereditoClass(item.veredito)">
                {{ item.veredito }}
              </span>
            </td>

            <td class="px-4 py-3">{{ item.data }}</td>

            <td class="px-4 py-3 flex items-center gap-2">
              <button class="p-2 bg-red-600 rounded text-white hover:bg-red-500 active:scale-95 transition">
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none">
                  <path
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M4 6h16M9 6V4h6v2M7 6v13a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V6M10 11v6M14 11v6"
                  />
                </svg>
              </button>

              <button class="p-2 bg-yellow-500 rounded text-white hover:bg-yellow-400 active:scale-95 transition">
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none">
                  <path stroke="currentColor" stroke-width="2" d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12Z"/>
                  <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
                </svg>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      search: '',
      selectedStatus: '',
      statusList: ['Aprovado', 'Rejeitado'],
      list: [
        {
          id: 'OS-MMWMH3RO',
          nome: 'Raimundo',
          tipo: 'Comprovante escolaridade',
          status: 'Aprovado',
          veredito: 'Autêntico',
          data: '18/03/2026 15:37'
        },
        {
          id: 'OS-X1YZ2Z3',
          nome: 'Raimundo',
          tipo: 'Cert. pós graduação',
          status: 'Rejeitado',
          veredito: 'Suspeito',
          data: '18/03/2026 16:52'
        }
      ]
    }
  },

  computed: {
    filteredList() {
      return this.list.filter(item => {
        const search = this.search.toLowerCase()

        const matchSearch =
          item.nome.toLowerCase().includes(search) ||
          item.id.toLowerCase().includes(search)

        const matchStatus =
          !this.selectedStatus || item.status === this.selectedStatus

        return matchSearch && matchStatus
      })
    }
  },

  methods: {
    handleStatus(status) {
      this.selectedStatus = status
    },

    statusClass(status) {
      return [
        'px-2 py-1 text-xs rounded-full font-semibold',
        status === 'Aprovado'
          ? 'bg-green-100 text-green-800'
          : 'bg-red-100 text-red-800'
      ]
    },

    vereditoClass(veredito) {
      return [
        'px-2 py-1 text-xs rounded-full font-semibold',
        veredito === 'Autêntico'
          ? 'bg-green-100 text-green-800'
          : 'bg-yellow-100 text-yellow-800'
      ]
    }
  }
}
</script>

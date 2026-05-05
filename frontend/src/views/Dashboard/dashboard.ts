export const stats = [
  { label: 'Total de Análises', value: '5', icon: '📄', iconBg: 'bg-blue-50', iconColor: 'text-blue-600' },
  { label: 'Aprovados', value: '2', icon: '✅', iconBg: 'bg-emerald-50', iconColor: 'text-emerald-600' },
  { label: 'Rejeitados', value: '2', icon: '❌', iconBg: 'bg-rose-50', iconColor: 'text-rose-600' },
  { label: 'Pendentes', value: '1', icon: '🕒', iconBg: 'bg-amber-50', iconColor: 'text-amber-600' },
];

export const recentAnalyses = [
  { 
    id: 'OS-MMWMH3RO', 
    document: 'Comprovante Escolaridade', 
    user: 'Sergio Luiz', 
    status: 'Rejeitado', 
    statusClass: 'bg-rose-100 text-rose-600',
    date: '18 mar'
  },
  { 
    id: 'OS-P7Q8R9', 
    document: 'Histórico Escolar', 
    user: 'Ana Oliveira', 
    status: 'Pendente', 
    statusClass: 'bg-amber-100 text-amber-600',
    date: '18 mar'
  },
  { 
    id: 'OS-X1Y2Z3', 
    document: 'Cert. Pós-Graduação', 
    user: 'Carlos Pereira', 
    status: 'Aprovado', 
    statusClass: 'bg-emerald-100 text-emerald-600',
    date: '18 mar'
  },
];

export const distribution = [
  { label: 'Aprovado', value: '2', color: 'bg-emerald-500' },
  { label: 'Rejeitado', value: '2', color: 'bg-rose-400' },
  { label: 'Pendente', value: '1', color: 'bg-amber-400' },
];

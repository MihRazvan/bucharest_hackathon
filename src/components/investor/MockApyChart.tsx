import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';

// Mock data for the APY chart
const mockData = [
  { name: 'Jan', apy: 9.2 },
  { name: 'Feb', apy: 9.5 },
  { name: 'Mar', apy: 10.1 },
  { name: 'Apr', apy: 9.8 },
  { name: 'May', apy: 10.3 },
  { name: 'Jun', apy: 10.7 },
  { name: 'Jul', apy: 11.2 },
  { name: 'Aug', apy: 11.0 },
  { name: 'Sep', apy: 11.5 },
  { name: 'Oct', apy: 11.8 },
  { name: 'Nov', apy: 11.4 },
  { name: 'Dec', apy: 11.8 }
];

export default function MockApyChart() {
  return (
    <div className="w-full h-[400px] bg-card/30 backdrop-blur-md p-6 rounded-lg shadow-md border border-white/10">
      <h3 className="text-lg font-medium mb-6 text-foreground">APY Performance</h3>
      <div className="h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={mockData}
            margin={{
              top: 10,
              right: 30,
              left: 10,
              bottom: 20,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis 
              dataKey="name"
              tick={{ fill: 'var(--muted-foreground)' }}
              dy={10}
            />
            <YAxis 
              tick={{ fill: 'var(--muted-foreground)' }}
              domain={[8, 12]}
              tickFormatter={(value) => `${value}%`}
              dx={-10}
            />
            <Tooltip 
              formatter={(value: number) => [`${value}%`, 'APY']}
              contentStyle={{
                backgroundColor: 'rgba(255,255,255,0.1)',
                backdropFilter: 'blur(8px)',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '4px',
                color: 'var(--foreground)'
              }}
            />
            <defs>
              <linearGradient id="apyGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#C3550B" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#C3550B" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <Area
              type="monotone"
              dataKey="apy"
              stroke="#C3550B"
              fill="url(#apyGradient)"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
} 
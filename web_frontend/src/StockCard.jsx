import React from 'react';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer } from 'recharts';
import { motion } from 'framer-motion';
import './App.css'; // Assuming you have some CSS for styling

const StockCard = ({ data }) => (
    <motion.div
        className="content-card"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
    >
        <h3>
            {data.ticker} - ${data.price}
        </h3>
        <div className={`change ${data.change > 0 ? 'positive' : 'negative'}`}>
            {data.change > 0 ? '↑' : '↓'} {Math.abs(data.change)}%
        </div>
        <ResponsiveContainer width="100%" height={50}>
            <LineChart data={data.sparkline}>
                <Line
                    type="monotone"
                    dataKey="y"
                    stroke="#00d4ff"
                    strokeWidth={2}
                    dot={false}
                />
            </LineChart>
        </ResponsiveContainer>
    </motion.div>
);

export default StockCard;
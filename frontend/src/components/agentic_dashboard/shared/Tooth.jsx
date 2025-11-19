import React from 'react';

const Tooth = ({ code, color, border, icon }) => (
  <div className={`w-8 h-10 ${color} border ${border} rounded-md flex flex-col items-center justify-center relative transition-all hover:scale-110 cursor-pointer`}>
     <span className="text-[8px] text-slate-400 absolute top-0.5">{code}</span>
     <div className="mt-2">{icon}</div>
  </div>
);

export default Tooth;

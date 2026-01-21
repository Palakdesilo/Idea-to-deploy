import { motion } from 'framer-motion';
import { Plus, Star } from 'lucide-react';
import Image from 'next/image';

interface ProductCardProps {
    title: string;
    price: number;
    imageUrl: string;
    category?: string;
    onAdd?: () => void;
}

export const ProductCard = ({ title, price, imageUrl, category = 'Product', onAdd }: ProductCardProps) => {
    return (
        <motion.div
            whileHover={{ y: -8 }}
            className="group relative w-full sm:w-[280px] h-[400px] flex flex-col"
        >
            <div className="glass rounded-[2rem] overflow-hidden h-full flex flex-col transition-all duration-500 hover:border-indigo-500/30 hover:shadow-2xl hover:shadow-indigo-500/10 bg-slate-900/50 border border-white/10">
                {/* Image Container */}
                <div className="relative aspect-square overflow-hidden bg-slate-900">
                    <img
                        src={imageUrl || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?q=80&w=1999&auto=format&fit=crop'}
                        alt={title}
                        className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-110"
                    />

                    {/* Badge */}
                    <div className="absolute top-4 left-4 px-3 py-1 bg-black/50 backdrop-blur-md border border-white/10 rounded-full">
                        <span className="text-[10px] font-bold uppercase tracking-widest text-indigo-300">
                            {category}
                        </span>
                    </div>

                    {/* Overlay Actions */}
                    {onAdd && (
                        <div className="absolute inset-0 bg-slate-950/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center gap-3">
                            <button
                                onClick={(e) => {
                                    e.preventDefault();
                                    onAdd();
                                }}
                                className="bg-white text-slate-950 px-6 py-3 rounded-2xl font-bold flex items-center gap-2 transform translate-y-4 group-hover:translate-y-0 transition-all duration-300 shadow-xl"
                            >
                                <Plus className="h-4 w-4" />
                                Quick Add
                            </button>
                        </div>
                    )}
                </div>

                {/* Product Info */}
                <div className="p-6 flex-1 flex flex-col">
                    <div className="flex items-center gap-1 mb-2">
                        {[...Array(5)].map((_, i) => (
                            <Star key={i} className={`h-3 w-3 ${i < 4 ? 'text-amber-400 fill-amber-400' : 'text-slate-600'}`} />
                        ))}
                        <span className="text-[10px] text-slate-500 ml-1 font-bold">4.8</span>
                    </div>

                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-indigo-400 transition-colors line-clamp-1">
                        {title}
                    </h3>

                    <div className="flex items-center justify-between mt-auto">
                        <div className="flex flex-col">
                            <span className="text-xs text-slate-500 font-bold uppercase tracking-wider">Price</span>
                            <span className="text-2xl font-black text-white">
                                ${price.toLocaleString()}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

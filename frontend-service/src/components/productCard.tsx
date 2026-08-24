import {Product} from '../types/productType';
import CButton from './button';


interface productCardProps{
    product:Product;
    addToCart:(product:Product)=>void;
}

export const ProductCard:React.FC<productCardProps>=({product,addToCart})=>{
return(
    <div className="group relative bg-white dark:bg-gray-800 rounded-2xl border border-gray-400 dark:border-gray-50 overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col justify between">
<div className="w-full aspect-square overflow-hidden bg-gray-100">
    {(product.isNew)&&(
        <span className="absolute top-3 left-3 z-10 bg-indigo-600 text-white text-xs font-semibold px-2.5 py-1 rounded-full shadow-md">
            New
        </span>
    )}
    <img src={product.image} alt={product.title} className='w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-500 '
    loading="lazy"/>
</div>

<div className='p-5 flexjustify-between flex-1 flex-col'>
<div>
    <span className="text-sm text-indigo-600 dark:text-indigo-400 font-medium tracking-wider">{product.category}</span>
    <h3 className="text-lg font-bold text-gray-900 dark:text-white">{product.title}</h3>
    <div className="flex items-center gap-1.5 mt-2">
        <span className="text-yellow-400 text-sm">★</span>
        <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">{product.rating}</span>
        <span className="text-xs text-gray-500 dark:text-gray-400">({product.reviewCount})</span>
    </div>
</div>

<div>
    <div>
<span className="text-xs text-gray-500 dark:text-gray-400 block">Price</span>
<span className="text-xl font-bold text-gray-900 dark:text-white">${product.price.toFixed(2)}</span>
    </div>
    <CButton onClick={() => addToCart(product)}>Add to Cart</CButton>
</div>
</div>
    </div>
)
}
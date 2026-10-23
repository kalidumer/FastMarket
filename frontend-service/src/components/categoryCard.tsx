import React from "react";
import{Category} from "../types/productType"


interface CategoryCardProps{
    category:Category;
    isSelected?:boolean;
    onClick?:()=>void;
}
export const CategoryCard :React.FC<CategoryCardProps>=(({category,isSelected,onClick})=>{
<div className={`group cursor-pointer relative overflow-hidden rounded-2xl p-4 transition-all duration-300 border ${
    isSelected? 'bg-indigo-50 border-indigo-500 dark:bg-indigo-950/40 dark:border-indigo-400 shadow-md'
        : 'bg-white border-gray-100 dark:bg-gray-900 dark:border-gray-800 hover:-translate-y-1 hover:shadow-lg'
}`}>
    <div className="aspect-square w-full overflow-hidden rounded-xl bg-gray-100 dark:bg-gray-800">
      <img
        src={category.image}
        alt={category.name}
        className="h-full w-full object-cover object-center group-hover:scale-105 transition-transform duration-300"
      />
    </div>
    <div className="mt-3 flex items-center justify-between">
      <h3 className="text-base font-bold text-gray-900 dark:text-white line-clamp-1">{category.name}</h3>
      <span className="text-xs font-semibold px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300">
        {category.itemCount}
      </span>
    </div>
</div>

})
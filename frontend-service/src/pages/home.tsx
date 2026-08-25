import { Product } from "../types/productType"
// import { MainLayout } from "../components/mainLayout"
import { MOCK_CATEGORIES, MOCK_PRODUCTS } from "../utils/fakedata"
import { ProductCard } from "../components/productCard"
import { useState } from "react"
import { useGetCategoriesQuery, useSearchProductsQuery } from "../features/product/productRtk"
import { CategoryCard } from "../components/categoryCard"

export const Home:React.FC=()=>{

  const handleAddToCart=(product:Product)=>{
console.log(`Added ${product.title} to cart`)
  }

  const [searchTerm,setSearchTerm]=useState('')
  const [selectedCategory,setSelectedCategory]=useState<string | undefined>(undefined)

  const {data:categories,isLoading:isCatLoading}=useGetCategoriesQuery();
  const {data:products ,isLoading:isProductLoading,isError}=useSearchProductsQuery({
    q:searchTerm || undefined,
    category_id:selectedCategory
  });

  return (
  <div className="min-h-screen bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-white pb-20">
      {/* HERO & SEARCH BAR */}
      <section className="relative overflow-hidden bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-800 py-16 px-6 text-white text-center rounded-b-[2.5rem] shadow-xl">
        <h1 className="text-3xl md:text-5xl font-black tracking-tight">Discover Premium Products</h1>
        <p className="mt-3 text-sm md:text-base text-indigo-100 max-w-xl mx-auto">
          Shop high quality collections delivered directly to your doorstep.
        </p>

        {/* Live Search Input */}
        <div className="mt-8 max-w-xl mx-auto">
          <div className="relative flex items-center">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search products by name or description..."
              className="w-full rounded-2xl bg-white px-5 py-3.5 pl-12 text-sm text-gray-900 placeholder-gray-400 shadow-lg focus:outline-none focus:ring-2 focus:ring-indigo-300"
            />
            <svg
              className="absolute left-4 h-5 w-5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="absolute right-4 text-xs font-semibold text-gray-400 hover:text-gray-600"
              >
                Clear
              </button>
            )}
          </div>
        </div>
      </section>

      <main className="max-w-7xl mx-auto px-6 mt-12 space-y-12">
        {/* CATEGORIES SECTION */}
        <section>
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-xl font-black tracking-tight">Browse Categories</h2>
              <p className="text-xs text-gray-500">Select a category to filter products</p>
            </div>
            {selectedCategory && (
              <button
                onClick={() => setSelectedCategory(undefined)}
                className="text-xs font-bold text-indigo-600 hover:text-indigo-800 dark:text-indigo-400"
              >
                Reset Filter
              </button>
            )}
          </div>

          {isCatLoading ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 animate-pulse">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-44 bg-gray-200 dark:bg-gray-800 rounded-2xl" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {categories?.map((cat) => (
                <CategoryCard
                  key={cat.id}
                  category={cat}
                  isSelected={selectedCategory === cat.id}
                  onClick={() =>
                    setSelectedCategory(selectedCategory === cat.id ? undefined : cat.id)
                  }
                />
              ))}
            </div>
          )}
        </section>

        {/* PRODUCTS SECTION */}
        <section>
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-xl font-black tracking-tight">
                {selectedCategory ? 'Filtered Products' : 'All Products'}
              </h2>
              <p className="text-xs text-gray-500">
                {products ? `Showing ${products.length} results` : 'Exploring catalog'}
              </p>
            </div>
          </div>

          {isProductLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 animate-pulse">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="h-80 bg-gray-200 dark:bg-gray-800 rounded-2xl" />
              ))}
            </div>
          ) : isError || !products || products.length === 0 ? (
            <div className="text-center py-16 bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800">
              <p className="text-gray-500 dark:text-gray-400 font-semibold">No products found.</p>
              <button
                onClick={() => {
                  setSearchTerm('');
                  setSelectedCategory(undefined);
                }}
                className="mt-4 px-4 py-2 bg-indigo-600 text-white text-xs font-bold rounded-xl"
              >
                Reset Search Filters
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {products.map((product) => (
                <ProductCard key={product.id} product={product} addToCart={handleAddToCart}/>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  )
}


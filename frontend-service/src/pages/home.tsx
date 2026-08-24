import { Product } from "../types/productType"
// import { MainLayout } from "../components/mainLayout"
import { MOCK_CATEGORIES, MOCK_PRODUCTS } from "../utils/fakedata"
import { ProductCard } from "../components/productCard"

export const Home:React.FC=()=>{

  const handleAddToCart=(product:Product)=>{
console.log(`Added ${product.title} to cart`)
  }
  return (
  <div className="space-y-12 pb-12">
    {/* Hero banner section */}
    <section>
      <div className="relative z-10 max-w-2xl space-y-6">
          <span className="inline-block px-3 py-1 bg-white/10 backdrop-blur-md rounded-full text-xs font-semibold tracking-wide uppercase text-indigo-200 border border-white/20">
            Exclusive Deals
          </span>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-tight">
            Elevate Your Digital Experience.
          </h1>
          <p className="text-indigo-100 text-lg sm:text-xl font-light leading-relaxed">
            Discover cutting-edge gadgets and premium lifestyle products delivered directly to your doorstep.
          </p>
          <div className="pt-2 flex flex-wrap gap-4">
            <button className="px-6 py-3.5 bg-white text-indigo-900 hover:bg-indigo-50 font-bold rounded-xl transition-all shadow-lg hover:shadow-xl">
              Shop Trending Items
            </button>
          </div>
        </div>
      </section>

      {/* CATEGORIES SECTION */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-gray-100">
            Shop by Category
          </h2>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          {MOCK_CATEGORIES.map((category) => (
            <div
              key={category.id}
              className="group relative h-48 rounded-2xl overflow-hidden cursor-pointer shadow-sm hover:shadow-md transition-shadow"
            >
              <img
                src={category.image}
                alt={category.name}
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent flex flex-col justify-end p-4">
                <h3 className="text-lg font-bold text-white">{category.name}</h3>
                <p className="text-xs text-gray-300">{category.itemCount}+ Products</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* FEATURED PRODUCTS GRID */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-gray-100">
            Featured Products
          </h2>
        </div>

        {/* Responsive Grid: 1 column on mobile, 2 on tablet, 4 on desktop */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {MOCK_PRODUCTS.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              addToCart={handleAddToCart}
            />
          ))}
        </div>
      </section>
  </div>
  )
}


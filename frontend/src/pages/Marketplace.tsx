import { useEffect, useState } from "react";
import { marketplaceAPI } from "../api/client";
import MarketplaceCard from "../components/MarketplaceCard";
import { ShoppingCart, Loader2, Filter } from "lucide-react";

interface Listing {
  id: string;
  seller_id: string;
  credit_id: string;
  price_per_ton: number;
  tons_available: number;
  status: string;
  listed_at: string;
  seller_name: string | null;
  field_name: string | null;
  methodology: string | null;
  vintage_year: number | null;
}

interface Transaction {
  id: string;
  listing_id: string;
  buyer_id: string;
  tons_purchased: number;
  total_usd: number;
  platform_fee: number;
  transaction_at: string;
}

export default function Marketplace() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [myTransactions, setMyTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<"browse" | "my">("browse");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [listingsRes, txRes] = await Promise.all([
        marketplaceAPI.list(),
        marketplaceAPI.myTransactions().catch(() => ({ data: [] })),
      ]);
      setListings(listingsRes.data || []);
      setMyTransactions(txRes.data || []);
    } catch {
      setListings([]);
    }
    setLoading(false);
  };

  const handleBuy = async (listingId: string, tons: number) => {
    try {
      await marketplaceAPI.buy(listingId, { tons_to_buy: tons });
      alert("Satın alma başarılı!");
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Satın alma hatası");
    }
  };

  const handleFilter = async () => {
    setLoading(true);
    try {
      const res = await marketplaceAPI.list({
        min_price: minPrice ? parseFloat(minPrice) : undefined,
        max_price: maxPrice ? parseFloat(maxPrice) : undefined,
      });
      setListings(res.data || []);
    } catch {
      setListings([]);
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-karbon-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Karbon Pazarı</h1>
        <p className="text-gray-500">Karbon kredisi alım ve satım platformu</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        <button
          onClick={() => setTab("browse")}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            tab === "browse"
              ? "bg-karbon-600 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          Satıştaki Krediler
        </button>
        <button
          onClick={() => setTab("my")}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            tab === "my"
              ? "bg-karbon-600 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          İşlemlerim
        </button>
      </div>

      {tab === "browse" && (
        <>
          {/* Filter */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
            <div className="flex flex-wrap gap-3 items-end">
              <div>
                <label className="block text-xs text-gray-500 mb-1">Min Fiyat ($/ton)</label>
                <input
                  type="number"
                  value={minPrice}
                  onChange={(e) => setMinPrice(e.target.value)}
                  className="px-3 py-2 border rounded-lg w-28 text-sm"
                  placeholder="0"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Max Fiyat ($/ton)</label>
                <input
                  type="number"
                  value={maxPrice}
                  onChange={(e) => setMaxPrice(e.target.value)}
                  className="px-3 py-2 border rounded-lg w-28 text-sm"
                  placeholder="100"
                />
              </div>
              <button
                onClick={handleFilter}
                className="bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded-lg flex items-center gap-2 text-sm"
              >
                <Filter className="w-4 h-4" />
                Filtrele
              </button>
            </div>
          </div>

          {/* Listings */}
          {listings.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center">
              <ShoppingCart className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p className="font-medium text-gray-600">Aktif ilan bulunamadı</p>
              <p className="text-sm text-gray-400 mt-1">
                Karbon kredilerinizi "Raporlar" sayfasından pazara çıkarabilirsiniz
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {listings.map((listing) => (
                <MarketplaceCard
                  key={listing.id}
                  listing={listing}
                  onBuy={handleBuy}
                />
              ))}
            </div>
          )}
        </>
      )}

      {tab === "my" && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100">
          <div className="p-5 border-b border-gray-100">
            <h2 className="font-semibold text-gray-800">Satın Alma İşlemlerim</h2>
          </div>
          {myTransactions.length === 0 ? (
            <div className="p-12 text-center text-gray-400">
              Henüz işlem yapılmamış
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="text-left p-3 font-medium text-gray-600">Tarih</th>
                    <th className="text-left p-3 font-medium text-gray-600">Miktar</th>
                    <th className="text-left p-3 font-medium text-gray-600">Toplam</th>
                    <th className="text-left p-3 font-medium text-gray-600">Komisyon</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {myTransactions.map((tx) => (
                    <tr key={tx.id} className="hover:bg-gray-50">
                      <td className="p-3">
                        {new Date(tx.transaction_at).toLocaleDateString("tr-TR")}
                      </td>
                      <td className="p-3 font-medium">{tx.tons_purchased} ton CO₂e</td>
                      <td className="p-3 text-karbon-600 font-semibold">
                        ${tx.total_usd.toFixed(2)}
                      </td>
                      <td className="p-3 text-gray-500">${tx.platform_fee.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

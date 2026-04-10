import { useState } from "react";
import { ShoppingCart, Leaf, Calendar } from "lucide-react";

interface Listing {
  id: string;
  price_per_ton: number;
  tons_available: number;
  seller_name: string | null;
  field_name: string | null;
  methodology: string | null;
  vintage_year: number | null;
}

interface Props {
  listing: Listing;
  onBuy: (listingId: string, tons: number) => void;
}

export default function MarketplaceCard({ listing, onBuy }: Props) {
  const [buyTons, setBuyTons] = useState("1");
  const [showBuy, setShowBuy] = useState(false);

  const totalPrice = parseFloat(buyTons || "0") * listing.price_per_ton;
  const fee = totalPrice * 0.035;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-karbon-50 rounded-lg flex items-center justify-center">
            <Leaf className="w-4 h-4 text-karbon-600" />
          </div>
          <div>
            <p className="font-medium text-sm text-gray-800">
              {listing.field_name || "Karbon Kredisi"}
            </p>
            <p className="text-xs text-gray-400">
              {listing.seller_name || "Satıcı"}
            </p>
          </div>
        </div>
        <span className="bg-karbon-50 text-karbon-700 px-2 py-0.5 rounded-full text-xs font-medium">
          {listing.methodology || "VM0042"}
        </span>
      </div>

      <div className="flex-1 space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-500">Fiyat</span>
          <span className="font-semibold text-karbon-700">${listing.price_per_ton}/ton</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Mevcut</span>
          <span className="font-medium">{listing.tons_available} ton CO₂e</span>
        </div>
        {listing.vintage_year && (
          <div className="flex justify-between">
            <span className="text-gray-500 flex items-center gap-1">
              <Calendar className="w-3 h-3" /> Vintage
            </span>
            <span className="font-medium">{listing.vintage_year}</span>
          </div>
        )}
      </div>

      {showBuy ? (
        <div className="mt-4 pt-4 border-t border-gray-100 space-y-3">
          <div>
            <label className="text-xs text-gray-500">Miktar (ton)</label>
            <input
              type="number"
              value={buyTons}
              onChange={(e) => setBuyTons(e.target.value)}
              min="0.1"
              max={listing.tons_available}
              step="0.1"
              className="w-full px-3 py-2 border rounded-lg text-sm mt-1"
            />
          </div>
          <div className="text-xs text-gray-500 space-y-1">
            <div className="flex justify-between">
              <span>Tutar:</span>
              <span>${totalPrice.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span>Komisyon (3.5%):</span>
              <span>${fee.toFixed(2)}</span>
            </div>
            <div className="flex justify-between font-semibold text-gray-700">
              <span>Toplam:</span>
              <span>${(totalPrice + fee).toFixed(2)}</span>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => onBuy(listing.id, parseFloat(buyTons))}
              className="flex-1 bg-karbon-600 hover:bg-karbon-700 text-white py-2 rounded-lg text-sm font-medium"
            >
              Satın Al
            </button>
            <button
              onClick={() => setShowBuy(false)}
              className="px-3 py-2 bg-gray-100 rounded-lg text-sm"
            >
              İptal
            </button>
          </div>
        </div>
      ) : (
        <button
          onClick={() => setShowBuy(true)}
          className="mt-4 w-full bg-karbon-50 hover:bg-karbon-100 text-karbon-700 py-2 rounded-lg flex items-center justify-center gap-2 text-sm font-medium transition-colors"
        >
          <ShoppingCart className="w-4 h-4" />
          Satın Al
        </button>
      )}
    </div>
  );
}

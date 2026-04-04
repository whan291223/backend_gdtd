import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router";
import { useLiffProfile } from "../hooks/useLiffProfile";
import { getPatientProfile } from "../api/patientApi";
import { getHistory } from "../api/spentNafApi";
import {
  logFood, getFoodByDate, deleteFood, updateFood,
  logExercise, getExerciseByDate, deleteExercise,
  getFoods,
  getNutritionTargets, // New API call
  type FoodLogRead, type ExerciseLogRead,
  type NutritionTargetRead // New Type
} from "../api/foodlogApi";

// --- Types -------------------------------------------------------------------

type MealCategory = "Breakfast" | "Lunch" | "Dinner" | "Snack" | "Drinking";

const CATEGORIES: MealCategory[] = ["Breakfast", "Lunch", "Dinner", "Snack", "Drinking"];
const FOOD_CATEGORIES: MealCategory[] = ["Breakfast", "Lunch", "Dinner", "Snack"];

const CAT_STYLE: Record<MealCategory, { dot: string; active: string; inactive: string }> = {
  Breakfast: { dot: "bg-amber-400",   active: "bg-amber-500/10 border-amber-500/50 text-amber-400",   inactive: "border-slate-200 text-slate-400" },
  Lunch:     { dot: "bg-emerald-400", active: "bg-emerald-500/10 border-emerald-500/50 text-emerald-400", inactive: "border-slate-200 text-slate-400" },
  Dinner:    { dot: "bg-violet-400",  active: "bg-violet-500/10 border-violet-500/50 text-violet-400",  inactive: "border-slate-200 text-slate-400" },
  Snack:     { dot: "bg-sky-400",     active: "bg-sky-500/10 border-sky-500/50 text-sky-400",     inactive: "border-slate-200 text-slate-400" },
  Drinking:  { dot: "bg-blue-400",    active: "bg-blue-500/10 border-blue-500/50 text-blue-400",    inactive: "border-slate-200 text-slate-400" },
};

const COMMON_EXERCISES = [
  { name: "เดิน",         met: 0.053 },
  { name: "วิ่ง",         met: 0.112 },
  { name: "ปั่นจักรยาน", met: 0.085 },
  { name: "ว่ายน้ำ",      met: 0.098 },
  { name: "โยคะ",         met: 0.042 },
  { name: "ยกน้ำหนัก",   met: 0.056 },
  { name: "เต้นแอโรบิก", met: 0.095 },
  { name: "อื่นๆ",        met: 0.060 },
];

// --- Helpers -----------------------------------------------------------------

function toDateStr(d: Date) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function formatDisplayDate(s: string) {
  const todayStr = toDateStr(new Date());
  const yest = new Date(); yest.setDate(yest.getDate() - 1);
  if (s === todayStr) return "วันนี้";
  if (s === toDateStr(yest)) return "เมื่อวาน";
  return new Date(s + "T00:00:00").toLocaleDateString("th-TH", { day: "numeric", month: "short", year: "numeric" });
}

// --- Floating label input component -----------------------------------------

interface FloatingInputProps {
  id: string;
  label: string;
  type?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  min?: number;
  step?: string;
  onFocus?: (e: React.FocusEvent<HTMLInputElement>) => void;
  className?: string;
}

function FloatingInput({
  id, label, type = "text", value, onChange,
  placeholder = " ", required, disabled, min, step, onFocus,
  className = "",
}: FloatingInputProps) {
  return (
    <div className="relative">
      <input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        onFocus={onFocus}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        min={min}
        step={step}
        className={`peer w-full rounded-xl px-4 pt-5 pb-2 text-sm text-gray-900 placeholder-transparent outline-none transition-all ${className}`}
      />
      <label
        htmlFor={id}
        className="absolute left-4 top-1 text-[10px] font-medium text-gray-400 peer-placeholder-shown:top-3.5 peer-placeholder-shown:text-sm peer-placeholder-shown:text-gray-400 peer-focus:top-1 peer-focus:text-[10px] peer-focus:text-amber-500 transition-all pointer-events-none"
      >
        {label}
      </label>
    </div>
  );
}

// --- Component ---------------------------------------------------------------

export function FoodLogPage() {
  const navigate = useNavigate();
  const { profile: liffProfile, isLoading: liffLoading } = useLiffProfile();

  // Date
  const [selectedDate, setSelectedDate] = useState(toDateStr(new Date()));

  // Data
  const [foodEntries, setFoodEntries]         = useState<FoodLogRead[]>([]);
  const [exerciseEntries, setExerciseEntries] = useState<ExerciseLogRead[]>([]);
  const [foodData, setFoodData]               = useState<Record<string, { calories: number; protein: number; sodium: number; potassium: number; phosphorus: number }>>({});

  // Patient context
  const [patientWeight, setPatientWeight]       = useState(0);
  const [patientBmi, setPatientBmi]             = useState(0);
  const [patientUrine, setPatientUrine]         = useState<number | null>(null);
  const [patientDiseases, setPatientDiseases]   = useState<string[]>([]);
  const [latestSpentScore, setLatestSpentScore] = useState(0);
  const [latestNafScore, setLatestNafScore]     = useState(0);
  const [nafLevel, setNafLevel]                 = useState<"unknown"|"low"|"moderate"|"high">("unknown");

  // Nutrition Targets (Now fetched from backend)
  const [targets, setTargets] = useState<NutritionTargetRead>({
    caloriesMin: 0, caloriesMax: 0,
    proteinMin: 0, proteinMax: 0,
    sodium: 2000, potassium: 2000, phosphorus: 800,
    waterMin: 500, waterMax: 800, isWaterRange: true
  });

  // New food form
  const [showFoodForm, setShowFoodForm]     = useState(false);
  const [newFoodName, setNewFoodName]       = useState("");
  const [newCalories, setNewCalories]       = useState("");
  const [newProtein, setNewProtein]         = useState("");
  const [newSodium, setNewSodium]           = useState("");
  const [newPotassium, setNewPotassium]     = useState("");
  const [newPhosphorus, setNewPhosphorus]   = useState("");
  const [newVolume, setNewVolume]           = useState("");
  const [newMealCat, setNewMealCat]         = useState<MealCategory>("Breakfast");
  const [suggestions, setSuggestions]       = useState<string[]>([]);
  const [matched, setMatched]               = useState(false);
  const [adding, setAdding]                 = useState(false);

  // New drink form
  const [showDrinkForm, setShowDrinkForm]   = useState(false);

  // New exercise form
  const [showExForm, setShowExForm]         = useState(false);
  const [newExName, setNewExName]           = useState("");
  const [newExDuration, setNewExDuration]   = useState("");
  const [newExBurned, setNewExBurned]       = useState("");
  const [exSuggestions, setExSuggestions]   = useState<string[]>([]);
  const [addingEx, setAddingEx]             = useState(false);

  // Inline edit — food
  const [editFoodId, setEditFoodId]         = useState<number | null>(null);
  const [editFoodName, setEditFoodName]     = useState("");
  const [editFoodCal, setEditFoodCal]       = useState("");
  const [editFoodProt, setEditFoodProt]     = useState("");
  const [editFoodSod, setEditFoodSod]       = useState("");
  const [editFoodPot, setEditFoodPot]       = useState("");
  const [editFoodPhos, setEditFoodPhos]     = useState("");
  const [editFoodVol, setEditFoodVol]       = useState("");
  const [editFoodCat, setEditFoodCat]       = useState<MealCategory>("Snack");
  const [editSaving, setEditSaving]         = useState(false);

  // UI
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState<string | null>(null);

  // --- Load on mount --------------------------------------------------------
  useEffect(() => {
    if (liffLoading || !liffProfile?.userId) return;
    const uid = liffProfile.userId;

    const init = async () => {
      try {
        const [profile, history, nutritionTargets] = await Promise.all([
          getPatientProfile(uid),
          getHistory(uid).catch(() => []),
          getNutritionTargets(uid).catch(() => null)
        ]);

        if (profile) {
          setPatientWeight(profile.weight ?? 0);
          setPatientBmi(profile.bmi ?? 0);
          setPatientUrine(profile.urineAmount ?? null);
          setPatientDiseases(profile.existingDiseases ?? []);
        }
        if (history.length > 0) {
          const latest = history[0];
          setLatestSpentScore(latest.spentScore ?? 0);
          setLatestNafScore(latest.nafScore ?? 0);
          const ns = latest.nafScore ?? 0;
          setNafLevel(ns >= 11 ? "high" : ns >= 6 ? "moderate" : ns > 0 ? "low" : "unknown");
        }
        if (nutritionTargets) {
          setTargets(nutritionTargets);
        }
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    };
    init();
  }, [liffProfile, liffLoading]);

  // --- Load food + exercise when date changes ------------------------------
  useEffect(() => {
    if (!liffProfile?.userId) return;
    const uid = liffProfile.userId;
    Promise.all([getFoodByDate(uid, selectedDate), getExerciseByDate(uid, selectedDate)])
      .then(([f, e]) => { setFoodEntries(f); setExerciseEntries(e); })
      .catch(e => setError(e.message));
  }, [liffProfile, selectedDate]);

  // --- Load food database ---------------------------------------------------
  useEffect(() => {
    getFoods().then(data => {
      const lookup: typeof foodData = {};
      data.forEach(f => { lookup[f.name] = { calories: f.calories, protein: f.protein, sodium: f.sodium, potassium: f.potassium, phosphorus: f.phosphorus }; });
      setFoodData(lookup);
    }).catch(() => {});
  }, []);

  // --- Totals ---------------------------------------------------------------
  const foodTotals = useMemo(() => foodEntries.reduce(
    (a, e) => ({
      calories: a.calories + e.calories,
      protein: a.protein + e.protein,
      sodium: a.sodium + e.sodium,
      potassium: a.potassium + e.potassium,
      phosphorus: a.phosphorus + e.phosphorus,
      volume: a.volume + (e.volume || 0)
    }),
    { calories: 0, protein: 0, sodium: 0, potassium: 0, phosphorus: 0, volume: 0 }
  ), [foodEntries]);

  const totalBurned = useMemo(() => exerciseEntries.reduce((a, e) => a + e.caloriesBurned, 0), [exerciseEntries]);
  const netCalories = foodTotals.calories - totalBurned;
  const isOverGoal  = netCalories > targets.caloriesMax;
  const pct         = targets.caloriesMax > 0 ? Math.min((netCalories / targets.caloriesMax) * 100, 100) : 0;

  const grouped = useMemo(() => CATEGORIES.reduce((acc, cat) => {
    acc[cat] = foodEntries.filter(e => e.mealCategory === cat);
    return acc;
  }, {} as Record<MealCategory, FoodLogRead[]>), [foodEntries]);

  // --- NAF recommendations -------------------------------------------------
  const nafRecs = useMemo(() => {
    if (nafLevel === "unknown") return [];
    if (nafLevel === "high") return ["อาหารให้พลังงานสูง (โยเกิร์ตเสริมโปรตีน, สมูทตี้โปรตีน)", "อาหารเคี้ยวง่าย/บดนิ่ม (โจ๊ก, ซุปครีม)", "พลังงานเสริม (ผลิตภัณฑ์เสริมอาหาร)"];
    if (nafLevel === "moderate") return ["เน้นโปรตีนคุณภาพ (ปลา ไก่ เต้าหู้)", "เพิ่มมื้อเล็กระหว่างวัน", "ใส่ไขมันดี (อะโวคาโด เมล็ดพืช)"];
    return ["ทานอาหารหลากหลายครบ 5 หมู่", "ควบคุมโซเดียมและน้ำตาล", "ดื่มน้ำให้เพียงพอ"];
  }, [nafLevel]);

  // --- Handlers -------------------------------------------------------------
  function shiftDate(days: number) {
    const d = new Date(selectedDate + "T00:00:00");
    d.setDate(d.getDate() + days);
    const next = toDateStr(d);
    if (next <= toDateStr(new Date())) setSelectedDate(next);
  }

  function handleFoodNameChange(name: string) {
    const trimmed = name.trim().toLowerCase();
    setSuggestions(trimmed ? Object.keys(foodData).filter(k => k.toLowerCase().includes(trimmed)).slice(0, 6) : []);
    const exact = Object.keys(foodData).find(k => k.toLowerCase() === trimmed);
    if (exact) {
      const f = foodData[exact];
      setMatched(true);
      setNewFoodName(exact);
      setNewCalories(String(f.calories)); setNewProtein(String(f.protein));
      setNewSodium(String(f.sodium)); setNewPotassium(String(f.potassium)); setNewPhosphorus(String(f.phosphorus));
    } else {
      setMatched(false);
      setNewFoodName(name);
    }
  }

  function pickSuggestion(item: string) {
    const f = foodData[item];
    setMatched(true); setNewFoodName(item); setSuggestions([]);
    setNewCalories(String(f.calories)); setNewProtein(String(f.protein));
    setNewSodium(String(f.sodium)); setNewPotassium(String(f.potassium)); setNewPhosphorus(String(f.phosphorus));
  }

  async function handleAddFood(e: React.FormEvent) {
    e.preventDefault();
    if (!liffProfile?.userId || !newFoodName || !newCalories) return;
    setAdding(true);
    try {
      const entry = await logFood(liffProfile.userId, {
        foodName: newFoodName, calories: parseFloat(newCalories),
        protein: parseFloat(newProtein) || 0, sodium: parseFloat(newSodium) || 0,
        potassium: parseFloat(newPotassium) || 0, phosphorus: parseFloat(newPhosphorus) || 0,
        volume: parseFloat(newVolume) || 0,
        mealCategory: newMealCat, eatenDate: selectedDate,
      });
      setFoodEntries(prev => [...prev, entry]);
      setNewFoodName(""); setNewCalories(""); setNewProtein(""); setNewSodium("");
      setNewPotassium(""); setNewPhosphorus(""); setNewVolume(""); setMatched(false); setSuggestions([]);
      setShowFoodForm(false);
      setShowDrinkForm(false);
    } catch (err: unknown) { setError(err instanceof Error ? err.message : "เกิดข้อผิดพลาด"); }
    finally { setAdding(false); }
  }

  async function handleDeleteFood(id: number) {
    if (!liffProfile?.userId) return;
    try {
      await deleteFood(liffProfile.userId, id);
      setFoodEntries(prev => prev.filter(e => e.id !== id));
    } catch (err: unknown) { setError(err instanceof Error ? err.message : "เกิดข้อผิดพลาด"); }
  }

  function startEditFood(entry: FoodLogRead) {
    setEditFoodId(entry.id);
    setEditFoodName(entry.foodName); setEditFoodCal(String(entry.calories));
    setEditFoodProt(String(entry.protein)); setEditFoodSod(String(entry.sodium));
    setEditFoodPot(String(entry.potassium)); setEditFoodPhos(String(entry.phosphorus));
    setEditFoodVol(String(entry.volume || 0));
    setEditFoodCat(entry.mealCategory as MealCategory);
  }

  async function handleSaveEditFood(id: number) {
    if (!liffProfile?.userId) return;
    setEditSaving(true);
    try {
      const updated = await updateFood(liffProfile.userId, id, {
        foodName: editFoodName, calories: parseFloat(editFoodCal),
        protein: parseFloat(editFoodProt) || 0, sodium: parseFloat(editFoodSod) || 0,
        potassium: parseFloat(editFoodPot) || 0, phosphorus: parseFloat(editFoodPhos) || 0,
        volume: parseFloat(editFoodVol) || 0,
        mealCategory: editFoodCat,
      });
      setFoodEntries(prev => prev.map(e => e.id === id ? updated : e));
      setEditFoodId(null);
    } catch (err: unknown) { setError(err instanceof Error ? err.message : "เกิดข้อผิดพลาด"); }
    finally { setEditSaving(false); }
  }

  async function handleAddExercise(e: React.FormEvent) {
    e.preventDefault();
    if (!liffProfile?.userId || !newExName || !newExDuration) return;
    const dur = parseInt(newExDuration);
    let burned = parseFloat(newExBurned);
    if (!burned && patientWeight > 0) {
      const met = COMMON_EXERCISES.find(ex => ex.name === newExName)?.met ?? 0.060;
      burned = Math.round(met * patientWeight * dur);
    }
    setAddingEx(true);
    try {
      const entry = await logExercise(liffProfile.userId, {
        exerciseName: newExName, durationMinutes: dur,
        caloriesBurned: burned, loggedDate: selectedDate,
      });
      setExerciseEntries(prev => [...prev, entry]);
      setNewExName(""); setNewExDuration(""); setNewExBurned(""); setShowExForm(false);
    } catch (err: unknown) { setError(err instanceof Error ? err.message : "เกิดข้อผิดพลาด"); }
    finally { setAddingEx(false); }
  }

  async function handleDeleteExercise(id: number) {
    if (!liffProfile?.userId) return;
    try {
      await deleteExercise(liffProfile.userId, id);
      setExerciseEntries(prev => prev.filter(e => e.id !== id));
    } catch (err: unknown) { setError(err instanceof Error ? err.message : "เกิดข้อผิดพลาด"); }
  }


  if (liffLoading || loading)
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
        <div className="w-10 h-10 rounded-full border-2 border-gray-300 border-t-amber-500 animate-spin" />
        <p className="mt-4 text-sm text-gray-400 tracking-widest uppercase">Loading</p>
      </div>
    );

  // --- Render ---------------------------------------------------------------
  return (
    <div className="min-h-screen bg-gray-50 px-4 py-10">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-96 h-64 bg-amber-500/8 rounded-full blur-3xl" />
      </div>

      <div className="relative max-w-sm mx-auto space-y-5">

        {/* Header */}
        <div className="flex items-center gap-3">
          <button onClick={() => navigate("/dashboard")}
            className="w-8 h-8 rounded-xl border border-gray-200 flex items-center justify-center text-gray-500 hover:text-gray-900 hover:border-gray-400 transition-all">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div>
            <p className="text-xs text-amber-500 uppercase tracking-[0.2em] font-medium">Nutrition</p>
            <h1 className="text-xl font-bold text-gray-900 tracking-tight">Food Log</h1>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-2xl px-4 py-3 flex items-center justify-between">
            <p className="text-red-600 text-xs">{error}</p>
            <button onClick={() => setError(null)} className="text-red-400 hover:text-red-600 ml-3 text-xs">✕</button>
          </div>
        )}

        {/* Date navigator */}
        <div className="flex items-center justify-between bg-white border border-gray-200 rounded-2xl px-4 py-3">
          <button onClick={() => shiftDate(-1)}
            className="w-8 h-8 rounded-lg border border-gray-200 flex items-center justify-center text-gray-500 hover:text-gray-900 hover:border-gray-400 transition-all">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div className="text-center">
            <p className="text-sm font-semibold text-gray-900">{formatDisplayDate(selectedDate)}</p>
            <p className="text-xs text-gray-600">{selectedDate}</p>
          </div>
          <button onClick={() => shiftDate(1)} disabled={selectedDate >= toDateStr(new Date())}
            className="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-400 hover:text-slate-900 hover:border-slate-400 disabled:opacity-30 disabled:cursor-not-allowed transition-all">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        {/* Calorie summary card */}
        <div className="bg-white border border-gray-200 rounded-3xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-400 uppercase tracking-widest">แคลอรี่สุทธิ</p>
              <div className="flex items-baseline gap-1.5 mt-0.5">
                <span className={`text-3xl font-bold ${isOverGoal ? "text-red-500" : "text-gray-900"}`}>
                  {Math.round(netCalories).toLocaleString()}
                </span>
                <span className="text-sm text-gray-400">
                  / {targets.caloriesMin.toLocaleString()} - {targets.caloriesMax.toLocaleString()} kcal
                </span>
              </div>
            </div>
          </div>

          {/* Progress bar */}
          <div className="space-y-1.5">
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <div className={`h-full rounded-full transition-all duration-500 ${isOverGoal ? "bg-red-500" : "bg-amber-500"}`}
                style={{ width: `${pct}%` }} />
            </div>
            <div className="flex justify-between text-xs text-slate-400">
              <span>{isOverGoal ? `เกิน ${Math.round(netCalories - targets.caloriesMax).toLocaleString()} kcal` : `ควรได้รับอีก ${Math.round(targets.caloriesMin - netCalories) > 0 ? Math.round(targets.caloriesMin - netCalories).toLocaleString() : 0} - ${Math.round(targets.caloriesMax - netCalories).toLocaleString()} kcal`}</span>
              <span>{Math.round(pct)}%</span>
            </div>
          </div>

          {/* Eat / Burn / Net row */}
          <div className="grid grid-cols-3 gap-2 pt-1">
            <div className="text-center bg-gray-50 border border-gray-100 rounded-xl p-2">
              <p className="text-xs text-gray-400 mb-0.5">กิน</p>
              <p className="text-sm font-bold text-gray-900">{Math.round(foodTotals.calories)}</p>
            </div>
            <div className="text-center bg-gray-50 border border-gray-100 rounded-xl p-2">
              <p className="text-xs text-gray-400 mb-0.5">เผา</p>
              <p className="text-sm font-bold text-orange-400">{Math.round(totalBurned)}</p>
            </div>
            <div className="text-center bg-gray-50 border border-gray-100 rounded-xl p-2">
              <p className="text-xs text-gray-400 mb-0.5">สุทธิ</p>
              <p className={`text-sm font-bold ${isOverGoal ? "text-red-500" : "text-emerald-600"}`}>{Math.round(netCalories)}</p>
            </div>
          </div>

          {/* Meal category mini totals */}
          <div className="grid grid-cols-5 gap-1">
            {CATEGORIES.map(cat => {
              const catTotal = grouped[cat]?.reduce((s, e) => s + e.calories, 0) || 0;
              return (
                <div key={cat} className="text-center space-y-1">
                  <div className={`w-2 h-2 rounded-full mx-auto ${CAT_STYLE[cat].dot}`} />
                  <p className="text-xs font-medium text-gray-800">{catTotal > 0 ? Math.round(catTotal) : "—"}</p>
                  <p className="text-[10px] text-gray-400">{cat}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Nutrition breakdown */}
        <div className="bg-white border border-gray-200 rounded-3xl p-5">
          <p className="text-xs text-gray-400 uppercase tracking-widest mb-3">สารอาหาร</p>
          <div className="space-y-3">
            {[
              { label: "โปรตีน", value: foodTotals.protein,    targetMin: targets.proteinMin, targetMax: targets.proteinMax, unit: "g",  color: "bg-blue-500", isRange: true },
              { label: "โซเดียม", value: foodTotals.sodium,     targetMax: targets.sodium,     unit: "mg", color: "bg-yellow-500" },
              { label: "โพแทสเซียม", value: foodTotals.potassium,  targetMax: targets.potassium,  unit: "mg", color: "bg-green-500" },
              { label: "ฟอสฟอรัส", value: foodTotals.phosphorus, targetMax: targets.phosphorus, unit: "mg", color: "bg-purple-500" },
              { label: "น้ำดื่มต่อวัน", value: 0, targetMin: targets.waterMin, targetMax: targets.waterMax, unit: "มล.", color: "bg-sky-400", isRange: targets.isWaterRange, hideProgress: true },
            ].map(({ label, value, targetMin, targetMax, unit, color, isRange, hideProgress }) => {
              const currentValue = label === "น้ำดื่มต่อวัน" ? foodTotals.volume : value;
              const displayTarget = isRange ? `${targetMin} - ${targetMax}` : (targetMax ? `<= ${targetMax}` : `${targetMin}`);
              const over = targetMax ? currentValue > targetMax : false;
              const p = targetMax ? Math.min((currentValue / targetMax) * 100, 100) : 0;

              return (
                <div key={label}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-600">{label}</span>
                    <span className={over ? "text-red-400" : "text-gray-400"}>
                      {Math.round(currentValue * 10) / 10} / {displayTarget} {unit}
                    </span>
                  </div>
                  {!hideProgress && (
                    <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full transition-all ${over ? "bg-red-500" : color}`} style={{ width: `${p}%` }} />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* NAF recommendations */}
        {nafRecs.length > 0 && (
          <div className="bg-white border border-gray-200 rounded-3xl p-5">
            <p className="text-xs text-amber-500 uppercase tracking-widest mb-3">
              คำแนะนำ NAF ({nafLevel === "high" ? "เสี่ยงสูง" : nafLevel === "moderate" ? "ปานกลาง" : "ต่ำ"})
            </p>
            <ul className="space-y-1.5">
              {nafRecs.map(r => (
                <li key={r} className="flex items-start gap-2 text-xs text-gray-600">
                  <span className="text-amber-500 mt-0.5">•</span>{r}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Add food/drink/exercise buttons & forms */}
        <div className="space-y-3">
          <button onClick={() => {
            const next = !showFoodForm;
            setShowFoodForm(next);
            if (next) {
              setShowDrinkForm(false);
              setShowExForm(false);
              setNewMealCat("Breakfast");
              setNewFoodName(""); setNewCalories(""); setNewProtein(""); setNewSodium("");
              setNewPotassium(""); setNewPhosphorus(""); setNewVolume("");
            }
          }}
            className={`w-full py-3 rounded-2xl border border-dashed transition-all text-sm ${showFoodForm ? "border-amber-500 text-amber-500" : "border-gray-300 text-gray-400 hover:border-amber-500/50 hover:text-amber-500"}`}>
            {showFoodForm ? "✕ ยกเลิกการเพิ่มอาหาร" : "+ เพิ่มรายการอาหาร"}
          </button>

          {showFoodForm && (
            <div className="bg-white border border-gray-200 rounded-3xl p-5 space-y-4 animate-in fade-in slide-in-from-top-2 duration-200">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold text-gray-900">ระบุรายละเอียดอาหาร</h2>
              </div>
              <form onSubmit={handleAddFood} className="space-y-3">
                {/* Meal category */}
                <div className="grid grid-cols-4 gap-1">
                  {FOOD_CATEGORIES.map(cat => (
                    <button key={cat} type="button" onClick={() => setNewMealCat(cat)}
                      className={`py-1.5 rounded-xl text-xs font-medium border transition-all ${newMealCat === cat ? CAT_STYLE[cat].active : CAT_STYLE[cat].inactive}`}>
                      {cat}
                    </button>
                  ))}
                </div>

                {/* Food name + autocomplete */}
                <div className="relative">
                  <FloatingInput
                    id="new-food-name"
                    label="ชื่ออาหาร *"
                    value={newFoodName}
                    onChange={e => handleFoodNameChange(e.target.value)}
                    required
                    className="bg-gray-50 border border-gray-200 hover:border-gray-400 focus:border-amber-500"
                  />
                  {suggestions.length > 0 && (
                    <div className="absolute z-10 left-0 right-0 mt-1 bg-white border border-gray-200 rounded-xl overflow-hidden shadow-xl">
                      {suggestions.map(item => (
                        <button key={item} type="button" onClick={() => pickSuggestion(item)}
                          className="w-full px-4 py-2.5 text-left text-sm text-gray-700 hover:bg-gray-50 transition-all">
                          {item}
                        </button>
                      ))}
                    </div>
                  )}
                  {matched && (
                    <p className="text-[10px] text-emerald-600 mt-1 px-1">✓ เติมข้อมูลจากฐานข้อมูลอัตโนมัติ — แก้ไขได้</p>
                  )}
                </div>

                {/* Nutrition fields */}
                <FloatingInput
                  id="new-calories-2"
                  label="แคลอรี่ (kcal) *"
                  type="number"
                  value={newCalories}
                  onChange={e => setNewCalories(e.target.value)}
                  required
                  min={0}
                  disabled={!newFoodName.trim()}
                  className="bg-gray-50 border border-gray-200 focus:border-amber-500 disabled:opacity-40 disabled:cursor-not-allowed"
                />

                <div className="grid grid-cols-2 gap-2">
                  {[
                    { id: "new-protein-2",    val: newProtein,    set: setNewProtein,    label: "โปรตีน (g)" },
                    { id: "new-sodium-2",     val: newSodium,     set: setNewSodium,     label: "โซเดียม (mg)" },
                    { id: "new-potassium-2",  val: newPotassium,  set: setNewPotassium,  label: "โพแทสเซียม (mg)" },
                    { id: "new-phosphorus-2", val: newPhosphorus, set: setNewPhosphorus, label: "ฟอสฟอรัส (mg)" },
                  ].map(({ id, val, set, label }) => (
                    <FloatingInput key={id} id={id} label={label} type="number" value={val}
                      onChange={e => set(e.target.value)} min={0}
                      disabled={!newFoodName.trim()}
                      className="bg-gray-50 border border-gray-200 focus:border-amber-500 disabled:opacity-40 disabled:cursor-not-allowed"
                    />
                  ))}
                </div>

                <button type="submit" disabled={adding || !newFoodName || !newCalories}
                  className="w-full py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 active:scale-95 disabled:opacity-40 text-gray-950 text-sm font-semibold transition-all">
                  {adding ? "กำลังเพิ่ม…" : "เพิ่มอาหาร"}
                </button>
              </form>
            </div>
          )}

          <button onClick={() => {
            const next = !showDrinkForm;
            setShowDrinkForm(next);
            if (next) {
              setShowFoodForm(false);
              setShowExForm(false);
              setNewMealCat("Drinking");
              setNewFoodName(""); setNewCalories(""); setNewProtein(""); setNewSodium("");
              setNewPotassium(""); setNewPhosphorus(""); setNewVolume("");
            }
          }}
            className={`w-full py-3 rounded-2xl border border-dashed transition-all text-sm ${showDrinkForm ? "border-sky-500 text-sky-500" : "border-gray-300 text-gray-400 hover:border-sky-500/50 hover:text-sky-500"}`}>
            {showDrinkForm ? "✕ ยกเลิกการเพิ่มเครื่องดื่ม" : "+ เพิ่มรายการเครื่องดื่ม"}
          </button>

          {showDrinkForm && (
            <div className="bg-white border border-gray-200 rounded-3xl p-5 space-y-4 animate-in fade-in slide-in-from-top-2 duration-200">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold text-gray-900">ระบุรายละเอียดเครื่องดื่ม</h2>
              </div>
              <form onSubmit={handleAddFood} className="space-y-3">
                <div className="relative">
                  <FloatingInput
                    id="new-drink-name"
                    label="ชื่อเครื่องดื่ม *"
                    value={newFoodName}
                    onChange={e => handleFoodNameChange(e.target.value)}
                    required
                    className="bg-gray-50 border border-gray-200 hover:border-gray-400 focus:border-sky-500"
                  />
                  {suggestions.length > 0 && (
                    <div className="absolute z-10 left-0 right-0 mt-1 bg-white border border-gray-200 rounded-xl overflow-hidden shadow-xl">
                      {suggestions.map(item => (
                        <button key={item} type="button" onClick={() => pickSuggestion(item)}
                          className="w-full px-4 py-2.5 text-left text-sm text-gray-700 hover:bg-gray-50 transition-all">
                          {item}
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <FloatingInput
                    id="new-drink-volume"
                    label="ปริมาณ (มล.) *"
                    type="number"
                    value={newVolume}
                    onChange={e => setNewVolume(e.target.value)}
                    required
                    min={0}
                    className="bg-gray-50 border border-gray-200 focus:border-sky-500"
                  />
                  <FloatingInput
                    id="new-drink-calories"
                    label="แคลอรี่ (kcal) *"
                    type="number"
                    value={newCalories}
                    onChange={e => setNewCalories(e.target.value)}
                    required
                    min={0}
                    className="bg-gray-50 border border-gray-200 focus:border-sky-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-2">
                  {[
                    { id: "new-drink-protein",    val: newProtein,    set: setNewProtein,    label: "โปรตีน (g)" },
                    { id: "new-drink-sodium",     val: newSodium,     set: setNewSodium,     label: "โซเดียม (mg)" },
                    { id: "new-drink-potassium",  val: newPotassium,  set: setNewPotassium,  label: "โพแทสเซียม (mg)" },
                    { id: "new-drink-phosphorus", val: newPhosphorus, set: setNewPhosphorus, label: "ฟอสฟอรัส (mg)" },
                  ].map(({ id, val, set, label }) => (
                    <FloatingInput key={id} id={id} label={label} type="number" value={val}
                      onChange={e => set(e.target.value)} min={0}
                      className="bg-gray-50 border border-gray-200 focus:border-sky-500"
                    />
                  ))}
                </div>

                <button type="submit" disabled={adding || !newFoodName || !newCalories || !newVolume}
                  className="w-full py-2.5 rounded-xl bg-sky-500 hover:bg-sky-400 active:scale-95 disabled:opacity-40 text-white text-sm font-semibold transition-all">
                  {adding ? "กำลังเพิ่ม…" : "เพิ่มเครื่องดื่ม"}
                </button>
              </form>
            </div>
          )}

          <button onClick={() => {
            const next = !showExForm;
            setShowExForm(next);
            if (next) {
              setShowFoodForm(false);
              setShowDrinkForm(false);
              setNewExName(""); setNewExDuration(""); setNewExBurned("");
            }
          }}
            className={`w-full py-3 rounded-2xl border border-dashed transition-all text-sm ${showExForm ? "border-orange-500 text-orange-500" : "border-gray-300 text-gray-400 hover:border-orange-500/50 hover:text-orange-500"}`}>
            {showExForm ? "✕ ยกเลิกบันทึกออกกำลังกาย" : "+ บันทึกการออกกำลังกาย"}
          </button>

          {showExForm && (
            <div className="bg-white border border-gray-200 rounded-3xl p-5 space-y-4 animate-in fade-in slide-in-from-top-2 duration-200">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold text-gray-900">ระบุรายละเอียดการออกกำลังกาย</h2>
              </div>
              <form onSubmit={handleAddExercise} className="space-y-3">
                <div className="relative">
                  <FloatingInput
                    id="ex-name"
                    label="ประเภทการออกกำลังกาย *"
                    value={newExName}
                    onChange={e => { setNewExName(e.target.value); setExSuggestions(e.target.value ? COMMON_EXERCISES.filter(ex => ex.name.includes(e.target.value)).map(ex => ex.name) : []); }}
                    required
                    className="bg-gray-50 border border-gray-200 focus:border-orange-500"
                  />
                  {exSuggestions.length > 0 && (
                    <div className="absolute z-10 left-0 right-0 mt-1 bg-white border border-gray-200 rounded-xl overflow-hidden shadow-xl">
                      {exSuggestions.map(name => (
                        <button key={name} type="button" onClick={() => { setNewExName(name); setExSuggestions([]); }}
                          className="w-full px-4 py-2.5 text-left text-sm text-gray-700 hover:bg-gray-50 transition-all">
                          {name}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                <FloatingInput
                  id="ex-duration"
                  label="ระยะเวลา (นาที) *"
                  type="number"
                  value={newExDuration}
                  required
                  min={1}
                  onChange={e => {
                    const dur = parseInt(e.target.value) || 0;
                    const met = COMMON_EXERCISES.find(ex => ex.name === newExName)?.met ?? 0.060;
                    if (patientWeight > 0 && dur > 0) setNewExBurned(String(Math.round(met * patientWeight * dur)));
                    setNewExDuration(e.target.value);
                  }}
                  className="bg-gray-50 border border-gray-200 focus:border-orange-500"
                />
                <FloatingInput
                  id="ex-burned"
                  label="แคลอรี่เผาผลาญ (kcal) — ประมาณอัตโนมัติ"
                  type="number"
                  value={newExBurned}
                  min={0}
                  onChange={e => setNewExBurned(e.target.value)}
                  className="bg-gray-50 border border-gray-200 focus:border-orange-500"
                />
                {patientWeight > 0 && <p className="text-[10px] text-gray-400 -mt-1 px-1">ประมาณจากน้ำหนัก {patientWeight} กก.</p>}
                <button type="submit" disabled={addingEx || !newExName || !newExDuration}
                  className="w-full py-2.5 rounded-xl bg-orange-500 hover:bg-orange-400 active:scale-95 disabled:opacity-40 text-white text-sm font-semibold transition-all">
                  {addingEx ? "กำลังเพิ่ม…" : "บันทึกการออกกำลังกาย"}
                </button>
              </form>
            </div>
          )}
        </div>

        {/* Food entries grouped by meal */}
        <div className="space-y-4">
          {CATEGORIES.map(cat => {
            const entries = grouped[cat];
            if (entries.length === 0) return null;
            return (
              <div key={cat} className="space-y-2">
                <div className="flex items-center gap-2 px-1">
                  <div className={`w-2 h-2 rounded-full ${CAT_STYLE[cat].dot}`} />
                  <span className="text-xs font-medium text-gray-500 uppercase tracking-widest">{cat}</span>
                  <span className="text-xs text-gray-400 ml-auto">{Math.round(entries.reduce((s, e) => s + e.calories, 0))} kcal</span>
                </div>
                {entries.map(entry => (
                  <div key={entry.id} className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
                    {editFoodId === entry.id ? (
                      <div className="p-4 space-y-3">
                        <div className="grid grid-cols-5 gap-1">
                          {CATEGORIES.map(c => (
                            <button key={c} type="button" onClick={() => setEditFoodCat(c)}
                              className={`py-1 rounded-lg text-xs border transition-all ${editFoodCat === c ? CAT_STYLE[c].active : CAT_STYLE[c].inactive}`}>
                              {c}
                            </button>
                          ))}
                        </div>
                        <FloatingInput
                          id="edit-food-name"
                          label="ชื่ออาหาร"
                          value={editFoodName}
                          onChange={e => setEditFoodName(e.target.value)}
                          className="bg-amber-50/60 border border-amber-200 focus:border-amber-500"
                        />
                        <FloatingInput
                          id="edit-food-cal"
                          label="แคลอรี่ (kcal)"
                          type="number"
                          value={editFoodCal}
                          onChange={e => setEditFoodCal(e.target.value)}
                          onFocus={e => e.target.select()}
                          className="bg-amber-50/60 border border-amber-200 focus:border-amber-500"
                        />
                        {editFoodCat === "Drinking" && (
                          <FloatingInput
                            id="edit-food-vol"
                            label="ปริมาณ (มล.)"
                            type="number"
                            value={editFoodVol}
                            onChange={e => setEditFoodVol(e.target.value)}
                            onFocus={e => e.target.select()}
                            className="bg-amber-50/60 border border-amber-200 focus:border-amber-500"
                          />
                        )}
                        <div className="grid grid-cols-2 gap-2">
                          {[
                            { id: "edit-prot",  val: editFoodProt, set: setEditFoodProt, label: "โปรตีน (g)" },
                            { id: "edit-sod",   val: editFoodSod,  set: setEditFoodSod,  label: "โซเดียม (mg)" },
                            { id: "edit-pot",   val: editFoodPot,  set: setEditFoodPot,  label: "โพแทสเซียม (mg)" },
                            { id: "edit-phos",  val: editFoodPhos, set: setEditFoodPhos, label: "ฟอสฟอรัส (mg)" },
                          ].map(({ id, val, set, label }) => (
                            <FloatingInput key={id} id={id} label={label} type="number" value={val}
                              onChange={e => set(e.target.value)}
                              onFocus={e => e.target.select()}
                              className="bg-amber-50/60 border border-amber-200 focus:border-amber-500"
                            />
                          ))}
                        </div>
                        <div className="flex gap-2">
                          <button onClick={() => setEditFoodId(null)}
                            className="flex-1 py-2 rounded-xl border border-gray-200 text-gray-500 text-xs hover:border-gray-400 transition-all">ยกเลิก</button>
                          <button onClick={() => handleSaveEditFood(entry.id)} disabled={editSaving}
                            className="flex-1 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 disabled:opacity-40 text-gray-950 text-xs font-semibold transition-all">
                            {editSaving ? "กำลังบันทึก…" : "บันทึก"}
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="px-4 py-3 flex items-center gap-3 bg-white">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className={`text-[10px] px-2 py-0.5 rounded-full border flex-shrink-0 ${
                              entry.mealCategory === "Breakfast" ? "bg-amber-50 border-amber-200 text-amber-600" :
                              entry.mealCategory === "Lunch"     ? "bg-emerald-50 border-emerald-200 text-emerald-600" :
                              entry.mealCategory === "Dinner"    ? "bg-violet-50 border-violet-200 text-violet-600" :
                              entry.mealCategory === "Snack"     ? "bg-sky-50 border-sky-200 text-sky-600" :
                                "bg-blue-50 border-blue-200 text-blue-600"
                            }`}>{entry.mealCategory}</span>
                            <p className="text-sm text-gray-900 font-medium truncate">{entry.foodName}</p>
                          </div>
                          <p className="text-xs text-gray-400 mt-0.5">
                            {Math.round(entry.calories * 100) / 100} kcal
                            {entry.volume > 0 && <span className="ml-2 text-sky-400">volume {Math.round(entry.volume * 100) / 100}ml</span>}
                            {entry.protein > 0 && <span className="ml-2 text-blue-400">Protein {Math.round(entry.protein * 100) / 100}g</span>}
                            {entry.sodium > 0 && <span className="ml-2 text-yellow-400">Na {Math.round(entry.sodium * 100) / 100}mg</span>}
                          </p>
                        </div>
                        <div className="flex items-center gap-1.5 shrink-0">
                          <button onClick={() => startEditFood(entry)}
                            className="w-7 h-7 rounded-lg border border-gray-200 flex items-center justify-center text-gray-400 hover:text-gray-900 hover:border-gray-400 transition-all">
                            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M15.232 5.232l3.536 3.536M9 13l6.5-6.5a2 2 0 012.828 2.828L11.828 15.828a2 2 0 01-1.414.586H9v-2a2 2 0 01.586-1.414z" />
                            </svg>
                          </button>
                          <button onClick={() => handleDeleteFood(entry.id)}
                            className="w-7 h-7 rounded-lg border border-gray-200 flex items-center justify-center text-gray-400 hover:text-red-500 hover:border-red-300 transition-all">
                            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6M9 7h6m-7 0a1 1 0 011-1h4a1 1 0 011 1m-7 0H5m14 0h-2" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            );
          })}

          {/* Exercise entries */}
          {exerciseEntries.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 px-1">
                <div className="w-2 h-2 rounded-full bg-orange-400" />
                <span className="text-xs font-medium text-gray-500 uppercase tracking-widest">Exercise</span>
                <span className="text-xs text-orange-500 ml-auto">-{Math.round(totalBurned)} kcal</span>
              </div>
              {exerciseEntries.map(entry => (
                <div key={entry.id} className="bg-white border border-gray-200 rounded-2xl px-4 py-3 flex items-center gap-3">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900 font-medium">{entry.exerciseName}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{entry.durationMinutes} นาที · <span className="text-orange-400">{Math.round(entry.caloriesBurned * 100)/ 100 } kcal เผาผลาญ</span></p>
                  </div>
                  <button onClick={() => handleDeleteExercise(entry.id)}
                    className="w-7 h-7 rounded-lg border border-gray-200 flex items-center justify-center text-gray-400 hover:text-red-500 hover:border-red-300 transition-all shrink-0">
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6M9 7h6m-7 0a1 1 0 011-1h4a1 1 0 011 1m-7 0H5m14 0h-2" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          )}

          {foodEntries.length === 0 && exerciseEntries.length === 0 && (
            <div className="text-center py-8 space-y-1">
              <p className="text-gray-400 text-sm">ยังไม่มีรายการสำหรับวันนี้</p>
              <p className="text-gray-400 text-xs">กด "+ เพิ่มรายการอาหาร" เพื่อเริ่มบันทึก</p>
            </div>
          )}
        </div>

        <p className="text-center text-xs text-gray-300 pb-4">powered by pluto solution</p>
      </div>
    </div>
  );
}

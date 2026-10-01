"use client";

import React, { useEffect, useState } from "react";
import { X, Sparkles, LogOut, CheckCircle2, RotateCcw } from "lucide-react";
import { AuthUser, UserProfile, fetchUserProfile } from "@/lib/api";

interface ProfileDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  user: AuthUser | null;
  onRetakeQuiz: () => void;
  onLogout: () => void;
}

export const ProfileDrawer: React.FC<ProfileDrawerProps> = ({
  isOpen,
  onClose,
  user,
  onRetakeQuiz,
  onLogout,
}) => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && user) {
      loadProfile();
    }
  }, [isOpen, user]);

  const loadProfile = async () => {
    setLoading(true);
    try {
      const data = await fetchUserProfile();
      setProfile(data);
    } catch (err) {
      console.error("Failed to load profile", err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/70 backdrop-blur-sm transition-all">
      <div className="w-full max-w-md h-full bg-[#0d1424] border-l border-slate-800 p-6 flex flex-col justify-between overflow-y-auto shadow-2xl">
        <div>
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold text-base">
                {user?.full_name ? user.full_name.charAt(0).toUpperCase() : user?.email.charAt(0).toUpperCase()}
              </div>
              <div>
                <h3 className="font-bold text-white text-base">{user?.full_name || "Reader Profile"}</h3>
                <p className="text-xs text-slate-400">{user?.email}</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Onboarding Status */}
          <div className="mb-6 p-4 rounded-xl bg-slate-900/80 border border-slate-800">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-slate-300">15-Question Calibration</span>
              {user?.completed_onboarding ? (
                <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                  <CheckCircle2 className="w-3 h-3" />
                  Active
                </span>
              ) : (
                <span className="text-[11px] font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full border border-amber-500/20">
                  Incomplete
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 mb-3">
              Your &quot;For You&quot; feed uses these weights to prioritize translations from Europe, Asia, Latin America, and the Middle East.
            </p>
            <button
              id="drawer-retake-quiz"
              onClick={() => {
                onClose();
                onRetakeQuiz();
              }}
              className="w-full py-2 rounded-xl bg-indigo-600/20 hover:bg-indigo-600 border border-indigo-500/40 text-indigo-300 hover:text-white text-xs font-bold transition-all flex items-center justify-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>{user?.completed_onboarding ? "Recalibrate Interest Graph" : "Take 15-Question Quiz"}</span>
            </button>
          </div>

          {/* Interest Weights Breakdown */}
          {loading ? (
            <div className="text-center py-6 text-xs text-slate-400">Loading interest weights...</div>
          ) : profile && profile.interest_weights ? (
            <div className="space-y-4">
              <div className="flex items-center gap-1.5 text-xs font-bold text-slate-200 uppercase tracking-wider">
                <Sparkles className="w-3.5 h-3.5 text-blue-400" />
                <span>Active Affinity Weights</span>
              </div>

              <div className="space-y-2.5 max-h-80 overflow-y-auto pr-1">
                {Object.entries(profile.interest_weights)
                  .sort((a, b) => b[1] - a[1])
                  .map(([key, weight]) => (
                    <div key={key} className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800/80">
                      <div className="flex justify-between text-xs font-medium mb-1">
                        <span className="text-slate-300 capitalize">{key.replace(":", " • ")}</span>
                        <span className="text-blue-400 font-bold">{Math.round(weight * 100)}%</span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-500 rounded-full"
                          style={{ width: `${Math.round(weight * 100)}%` }}
                        />
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          ) : null}
        </div>

        {/* Footer Logout */}
        <div className="pt-4 border-t border-slate-800">
          <button
            onClick={() => {
              onClose();
              onLogout();
            }}
            className="w-full py-2.5 rounded-xl bg-rose-600/10 hover:bg-rose-600 border border-rose-500/30 text-rose-300 hover:text-white text-xs font-bold transition-all flex items-center justify-center gap-2"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out</span>
          </button>
        </div>
      </div>
    </div>
  );
};

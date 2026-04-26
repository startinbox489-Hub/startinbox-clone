import {
	IdeaStoreStateI,
	TempIdeaT,
} from '@/components/Landing/ValidateIdeaSection/interface';
import { create } from 'zustand';

export const useIdeaStoreState = create<IdeaStoreStateI>((set) => ({
	ideas: [],
	pushIdea: (idea) => set((state) => ({ ideas: [...state.ideas, idea] })),
	popIdea: (ideaId) =>
		set((state) => ({
			ideas: state.ideas.filter((idea) => idea.id !== ideaId),
		})),
	clearIdeas: () => set({ ideas: [] }),
	tempIdea: undefined,
	clearTemIdea: () => set({ tempIdea: undefined }),
	addTempIdea: (newTempIdea: TempIdeaT) => set({ tempIdea: newTempIdea }),
}));

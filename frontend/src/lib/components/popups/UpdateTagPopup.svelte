<script lang="ts">
	import { project, selectionIds, selections, tagIds, tags } from '$lib/stores';
	import type { Tag, ZenoService } from '$lib/zenoapi';
	import Button from '@smui/button';
	import { Content } from '@smui/paper';
	import { createEventDispatcher, getContext } from 'svelte';
	import Popup from './Popup.svelte';

	const dispatch = createEventDispatcher();
	const zenoClient = getContext('zenoClient') as ZenoService;

	let selectedTag: Tag | undefined;

	function addToTag() {
		if (selectedTag === undefined) return;
		selectedTag.dataIds = [...new Set([...selectedTag.dataIds, ...$selectionIds])];
		zenoClient.updateTag($project.uuid, selectedTag).then(() => {
			tags.update((t) => {
				const index = t.findIndex((tag) => tag.id === selectedTag?.id);
				if (index !== -1 && selectedTag !== undefined) {
					t[index] = selectedTag;
				}
				return t;
			});
			let s = new Set<string>();
			$selections.tags.forEach((tagId) => {
				const tag: Tag | undefined = $tags.find((cur) => cur.id === tagId);
				if (tag !== undefined) tag.dataIds.forEach((item) => s.add(item));
				tagIds.set([...s]);
			});
			selectionIds.set([]);
			dispatch('close');
		});
	}

	function submit(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			dispatch('close');
		}
		if (e.key === 'Enter') {
			addToTag();
		}
	}
</script>

<svelte:window on:keydown={submit} />

<Popup on:close>
	<Content style="display: flex; align-items: center;">
		<select class="x-2 h-full" bind:value={selectedTag}>
			{#each $tags as tag}
				<option value={tag}>{tag.tagName}</option>
			{/each}
		</select>
		<Button style="margin-left: 10px;" variant="outlined" on:click={() => dispatch('close')}
			>Cancel</Button
		>
		<Button style="margin-left: 5px;" variant="outlined" on:click={() => addToTag()}>Add</Button>
	</Content>
	{#if $selectionIds !== undefined && $selectionIds.length > 0}
		<p style:margin-right="10px">
			{$selectionIds.length} instance{$selectionIds.length > 1 ? 's' : ''} selected
		</p>
	{/if}
</Popup>

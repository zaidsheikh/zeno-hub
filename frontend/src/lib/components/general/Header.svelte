<script lang="ts">
	import { page } from '$app/stores';
	import type { Report, User, ZenoService } from '$lib/zenoapi';
	import { mdiFileChartOutline, mdiPlus } from '@mdi/js';
	import Button from '@smui/button';
	import { getContext } from 'svelte';
	import LikeButton from './LikeButton.svelte';
	import UserButton from './UserButton.svelte';

	export let user: User | null = null;
	export let report: Report | null = null;
	export let showNewReport = false;
	export let numLikes = 0;
	export let userLiked = false;
	export let reportEdit = false;

	const zenoClient = getContext('zenoClient') as ZenoService;
</script>

<div class="mx-6 my-5 flex h-8 items-center justify-between">
	<div class="flex h-full items-center">
		<a href="/" class="shrink-0">
			<img src="/zeno-logo.png" class="h-8" alt="diamond tesselation logo" />
		</a>
		{#if $page.route.id?.startsWith('/(app)/home/')}
			<div class="flex h-full md:ml-2 md:mt-0">
				<Button class="h-full" on:click={() => (showNewReport = true)}>
					<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="mr-2 w-6 fill-primary">
						<path d={mdiPlus} />
					</svg>
					New Report
				</Button>
			</div>
		{/if}
		{#if report}
			<div class="ml-5 hidden items-center sm:flex">
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class=" w-6 fill-grey-dark">
					<path d={mdiFileChartOutline} />
				</svg>
				<p class="ml-1 mr-6 text-grey-dark">{report.name}</p>
				<LikeButton
					on:like={() => (report ? zenoClient.likeReport(report.id) : '')}
					{user}
					likes={numLikes}
					liked={userLiked}
				/>
			</div>
		{/if}
	</div>
	<div class="flex h-full shrink-0 items-center">
		{#if report && report.editor}
			<Button
				class="mr-4 mt-2 shrink-0 sm:mt-0"
				variant="outlined"
				on:click={() => (reportEdit = true)}>Settings</Button
			>
		{/if}
		<UserButton {user} />
	</div>
</div>

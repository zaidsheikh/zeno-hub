<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { tooltip } from '$lib/util/tooltip';
	import type { User } from '$lib/zenoapi';
	import Button from '@smui/button';

	export let user: User | null;

	const exploreTab = $page.route.id === '/(app)/home';
</script>

{#if user}
	{#if $page.route.id?.startsWith('/(app)/home')}
		<Button
			class="mr-3 h-full"
			variant="outlined"
			on:click={() => (exploreTab ? goto('/') : goto('/home'))}
			>{exploreTab ? 'My Hub' : 'Explore'}</Button
		>
	{/if}
	<button
		class="flex h-10 w-10 items-center justify-center rounded-full bg-primary-dark font-extrabold capitalize text-white transition hover:bg-primary"
		use:tooltip={{ text: 'Account Settings' }}
		on:click={() => goto('/account')}
	>
		{user.name.slice(0, 2)}
	</button>
{:else}
	<div class="h-8">
		<Button class="mr-3 h-full" variant="raised" on:click={() => goto('/signup')}>Sign Up</Button>
		<Button class="h-full" variant="outlined" on:click={() => goto('/login')}>Log In</Button>
	</div>
{/if}

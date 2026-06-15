<template>
  <div class="vk-listing-card" @click="$emit('click')">
    <div class="vk-listing-card__header">
      <Badge :variant="listingType === 'sell' ? 'info' : 'warn'" size="sm">
        {{ listingType === 'sell' ? '出售' : '求购' }}
      </Badge>
      <span class="vk-listing-card__views">{{ viewsCount }} 次浏览</span>
    </div>
    <h3 class="vk-listing-card__title">{{ title }}</h3>
    <div class="vk-listing-card__specs">
      <span v-if="material" class="vk-listing-card__spec">{{ material }}</span>
      <span v-if="thickness" class="vk-listing-card__spec">{{ thickness }}mm</span>
      <span v-if="dimensions" class="vk-listing-card__spec">{{ dimensions }}</span>
      <span v-if="surface" class="vk-listing-card__spec">{{ surface }}</span>
    </div>
    <div class="vk-listing-card__footer">
      <div class="vk-listing-card__price">
        <PriceDisplay :value="price" size="md" />
        <span class="vk-listing-card__unit">/ {{ unit }}</span>
      </div>
      <div class="vk-listing-card__meta">
        <span class="vk-listing-card__location" v-if="location">
          <MapPin :size="12" /> {{ location }}
        </span>
        <span class="vk-listing-card__qty">库存 {{ quantity }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { MapPin } from 'lucide-vue-next';
import Badge from '../base/Badge.vue';
import PriceDisplay from '../data/PriceDisplay.vue';

interface Props {
  title: string;
  listingType: 'sell' | 'buy';
  price: number;
  unit?: string;
  material?: string;
  thickness?: number;
  dimensions?: string;
  surface?: string;
  quantity?: number;
  location?: string;
  viewsCount?: number;
}

withDefaults(defineProps<Props>(), {
  unit: '件',
  material: '',
  thickness: 0,
  dimensions: '',
  surface: '',
  quantity: 0,
  location: '',
  viewsCount: 0,
});

defineEmits<{ click: [] }>();
</script>

<style scoped>
.vk-listing-card {
  padding: 16px;
  border-radius: var(--r-card);
  background: var(--surface);
  border: 1px solid var(--border);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.vk-listing-card:hover {
  border-color: var(--brand);
  box-shadow: var(--sh-sm);
}

.vk-listing-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.vk-listing-card__views {
  font-size: var(--fz-xs);
  color: var(--text-faint);
}

.vk-listing-card__title {
  font-size: var(--fz-body);
  font-weight: var(--fw-semibold);
  color: var(--text);
  margin: 0 0 10px;
  line-height: var(--lh-relaxed);
}

.vk-listing-card__specs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 14px;
}

.vk-listing-card__spec {
  font-size: var(--fz-xs);
  padding: 2px 8px;
  border-radius: var(--r-tag);
  background: var(--surface-sunken);
  color: var(--text-muted);
}

.vk-listing-card__footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.vk-listing-card__unit {
  font-size: var(--fz-sm);
  color: var(--text-muted);
  margin-left: 2px;
}

.vk-listing-card__meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
  font-size: var(--fz-xs);
  color: var(--text-faint);
}

.vk-listing-card__location {
  display: flex;
  align-items: center;
  gap: 2px;
}

.vk-listing-card__qty {
  color: var(--text-muted);
}
</style>

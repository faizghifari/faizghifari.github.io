import { defineCollection, z } from 'astro:content';

const blogCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.coerce.date(),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
    // Optional cover image for the post (path relative to public/ or absolute URL)
    cover: z.string().optional(),
    // Whether to hide the cover on the listing page
    coverPosition: z.enum(['top', 'middle', 'bottom']).default('top'),
    // Post format: 'article' (default long-form), 'note' (short update), 'photo' (image-heavy)
    format: z.enum(['article', 'note', 'photo']).default('article'),
  }),
});

export const collections = {
  blog: blogCollection,
};

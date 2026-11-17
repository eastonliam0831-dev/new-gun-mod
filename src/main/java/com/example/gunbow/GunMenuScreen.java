package com.example.gunbow;

import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

/** Paged button grid for picking a gun skin. Built only from buttons (no custom drawing). */
public class GunMenuScreen extends Screen {
    private final Screen parent;
    private int page = 0;
    private String current;
    private boolean loaded = false;

    public GunMenuScreen(Screen parent) {
        super(Component.literal("Choose your bow skin"));
        this.parent = parent;
    }

    @Override
    protected void init() {
        if (!loaded) { current = GunBowClient.currentSlug(this.minecraft); loaded = true; }

        String[][] guns = GunBowClient.GUNS;
        int cols = 3, gap = 4, bh = 20;
        int bw = Math.min(150, (this.width - 20 - gap * (cols - 1)) / cols);
        int top = 34;
        int rows = Math.max(3, (this.height - top - 36) / (bh + gap));
        int per = cols * rows;
        int pages = (guns.length + per - 1) / per;
        if (page > pages - 1) page = pages - 1;
        int left = (this.width - (bw * cols + gap * (cols - 1))) / 2;

        Button header = Button.builder(this.getTitle(), b -> {}).bounds(this.width / 2 - 100, 8, 200, 20).build();
        header.active = false;
        this.addRenderableWidget(header);

        for (int i = 0; i < per; i++) {
            int idx = page * per + i;
            if (idx >= guns.length) break;
            final String slug = guns[idx][0];
            boolean sel = slug.equals(current);
            Component label = Component.literal((sel ? "> " : "") + guns[idx][1] + (sel ? " <" : ""));
            int x = left + (i % cols) * (bw + gap);
            int y = top + (i / cols) * (bh + gap);
            this.addRenderableWidget(Button.builder(label, b -> {
                current = slug;
                GunBowClient.select(this.minecraft, slug);
                this.rebuildWidgets();
            }).bounds(x, y, bw, bh).build());
        }

        int by = this.height - 28;
        int total = 70 + 110 + 70 + 70 + gap * 3;
        int bx = (this.width - total) / 2;

        Button prev = Button.builder(Component.literal("< Prev"), b -> { page--; this.rebuildWidgets(); })
                .bounds(bx, by, 70, bh).build();
        prev.active = page > 0;
        this.addRenderableWidget(prev);

        this.addRenderableWidget(Button.builder(Component.literal("Vanilla bow"), b -> {
            current = null;
            GunBowClient.select(this.minecraft, null);
            this.rebuildWidgets();
        }).bounds(bx + 70 + gap, by, 110, bh).build());

        Button next = Button.builder(Component.literal("Next > " + (page + 1) + "/" + pages), b -> { page++; this.rebuildWidgets(); })
                .bounds(bx + 70 + 110 + gap * 2, by, 70, bh).build();
        next.active = page < pages - 1;
        this.addRenderableWidget(next);

        this.addRenderableWidget(Button.builder(Component.literal("Done"), b -> this.onClose())
                .bounds(bx + 70 + 110 + 70 + gap * 3, by, 70, bh).build());
    }

    @Override
    public void onClose() {
        this.minecraft.gui.setScreen(this.parent);
    }
}

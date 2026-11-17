package com.example.gunbow;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.keymapping.v1.KeyMappingHelper;
import net.fabricmc.fabric.api.resource.v1.ResourceLoader;
import net.fabricmc.fabric.api.resource.v1.pack.PackActivationType;
import net.fabricmc.loader.api.FabricLoader;
import net.fabricmc.loader.api.ModContainer;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.packs.repository.PackRepository;

import java.io.InputStreamReader;
import java.io.Reader;
import java.util.*;

/**
 * One optional built-in resource pack per gun (each replaces the bow's model).
 * Keys: K = menu, G = next, H = previous, J = vanilla bow.
 */
public class GunBowClient implements ClientModInitializer {
    public static final String MOD_ID = "gunbow";
    /** {slug, display name}, in the order of the original list. */
    public static final String[][] GUNS = loadGuns();

    private static KeyMapping next, prev, reset, menu;

    @Override
    public void onInitializeClient() {
        ModContainer self = FabricLoader.getInstance().getModContainer(MOD_ID).orElseThrow();

        for (String[] g : GUNS) {
            ResourceLoader.registerBuiltinPack(
                Identifier.fromNamespaceAndPath(MOD_ID, g[0]), self,
                Component.literal("Bow: " + g[1]), PackActivationType.NORMAL);
        }

        KeyMapping.Category cat = KeyMapping.Category.register(Identifier.fromNamespaceAndPath(MOD_ID, "main"));
        menu  = KeyMappingHelper.registerKeyMapping(new KeyMapping("key.gunbow.menu",  75, cat)); // K
        next  = KeyMappingHelper.registerKeyMapping(new KeyMapping("key.gunbow.next",  71, cat)); // G
        prev  = KeyMappingHelper.registerKeyMapping(new KeyMapping("key.gunbow.prev",  72, cat)); // H
        reset = KeyMappingHelper.registerKeyMapping(new KeyMapping("key.gunbow.reset", 74, cat)); // J

        ClientTickEvents.END_CLIENT_TICK.register(mc -> {
            while (menu.consumeClick()) {
                if (mc.player != null && mc.gui.screen() == null) mc.gui.setScreen(new GunMenuScreen(null));
            }
            while (next.consumeClick())  cycle(mc, +1);
            while (prev.consumeClick())  cycle(mc, -1);
            while (reset.consumeClick()) { select(mc, null); say(mc, "Bow skin: vanilla"); }
        });
    }

    private static boolean matches(String packId, String slug) {
        if (!packId.contains(MOD_ID) || !packId.endsWith(slug)) return false;
        int before = packId.length() - slug.length() - 1;
        if (before < 0) return true;
        char c = packId.charAt(before);
        return !Character.isLetterOrDigit(c) && c != '_';
    }

    /** Slug of the currently enabled gun skin, or null for the vanilla bow. */
    public static String currentSlug(Minecraft mc) {
        PackRepository repo = mc.getResourcePackRepository();
        for (String id : repo.getSelectedIds())
            for (String[] g : GUNS) if (matches(id, g[0])) return g[0];
        return null;
    }

    /** Enable the gun skin with this slug (null = vanilla bow). Saves options and reloads resources. */
    public static void select(Minecraft mc, String slug) {
        PackRepository repo = mc.getResourcePackRepository();
        repo.reload();
        List<String> selected = new ArrayList<>(repo.getSelectedIds());
        selected.removeIf(id -> id.contains(MOD_ID));
        if (slug != null) {
            for (String id : repo.getAvailableIds()) {
                if (matches(id, slug)) { selected.add(id); break; }   // last = highest priority
            }
        }
        repo.setSelected(selected);
        mc.options.updateResourcePacks(repo);
    }

    private static void cycle(Minecraft mc, int dir) {
        String cur = currentSlug(mc);
        int i = -1;
        for (int k = 0; k < GUNS.length; k++) if (GUNS[k][0].equals(cur)) i = k;
        int n = i < 0 ? (dir > 0 ? 0 : GUNS.length - 1) : Math.floorMod(i + dir, GUNS.length);
        select(mc, GUNS[n][0]);
        say(mc, "Bow skin: " + GUNS[n][1] + " (" + (n + 1) + "/" + GUNS.length + ")");
    }

    private static void say(Minecraft mc, String text) {
        if (mc.player != null) mc.player.sendSystemMessage(Component.literal(text));
    }

    private static String[][] loadGuns() {
        try (Reader r = new InputStreamReader(GunBowClient.class.getResourceAsStream("/guns.json"))) {
            var arr = com.google.gson.JsonParser.parseReader(r).getAsJsonArray();
            String[][] out = new String[arr.size()][];
            for (int i = 0; i < out.length; i++) {
                var p = arr.get(i).getAsJsonArray();
                out[i] = new String[]{p.get(0).getAsString(), p.get(1).getAsString()};
            }
            return out;
        } catch (Exception e) { throw new RuntimeException("guns.json missing", e); }
    }
}
